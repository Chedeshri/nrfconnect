from time import sleep
from typing import List, Tuple

from pc_ble_driver_py import config

config.__conn_ic_id__ = "NRF52"

from pc_ble_driver_py.ble_adapter import BLEAdapter, BLEDriverObserver, BLEAdvData, BLEGapAddr, BLEUUID, BLEGapRoles, \
    BLEUUIDBase, BLEAdapterObserver
from pc_ble_driver_py.ble_driver import BLEGapScanParams, BLEDriver


class NrfBackend:
    mac_string_to_bin = lambda mac: list(map(lambda x: int(x, 16), mac.split(":")))
    mac_bin_to_string = lambda mac: ":".join("{0:02X}".format(b) for b in mac)

    def __init__(self, adapter: str = 'hci0', address_type: str = 'public'):
        """Create new instance of the backend."""
        # super(BluepyBackend, self).__init__(adapter, address_type)
        self._adapter = BLEAdapter(
            BLEDriver(
                serial_port=adapter, auto_flash=False, baud_rate=1000000, log_severity_level="info"
            )
        )
        self._adapter.driver.open()
        self._adapter.driver.ble_enable()
        self._connection = None

    def write_handle(self, handle: int, value: bytes, uuid_type: int = 1):
        """Write a value to a handle.
        You must be connected to a device first."""
        self._adapter.write_req(self._connection, BLEUUID(handle, BLEUUIDBase(uuid_type=uuid_type)), value)

    def read_handle(self, handle: int, uuid_type: int = 1) -> bytes:
        """Read a handle from the device.
        You must be connected to do this.
        """
        return self._adapter.read_req(self._connection, BLEUUID(handle, BLEUUIDBase(uuid_type=uuid_type)))

    def wait_for_notification(self, handle: int, delegate, notification_timeout: float, uuid_type: int = 1):
        """ registers as a listener and calls the delegate's handleNotification
            for each notification received
            @param handle - the handle to use to register for notifications
            @param delegate - the delegate object's handleNotification is called for every notification received
            @param notification_timeout - wait this amount of seconds for notifications
        """

        class NoticationObserver(BLEAdapterObserver):
            def on_notification(self, ble_adapter, conn_handle, uuid, data):
                if uuid == BLEUUID(handle, BLEUUIDBase(uuid_type=uuid_type)):
                    delegate.handleNotification(handle, data)

        observer = NoticationObserver()
        self._adapter.observer_register(observer)
        return self._adapter.enable_notification(self._connection, BLEUUID(handle, BLEUUIDBase(uuid_type=uuid_type)))

    def connect(self, mac: str):
        """Connect to a device."""
        print("connected to DD:A9:BB:27:C8:C8")

        class ConnectionObserver(BLEDriverObserver):

            def __init__(self):
                self.connected = False
                self.connection_id = None

            def on_gap_evt_connected(
                    self, ble_driver, conn_handle, peer_addr, role, conn_params
            ):
                self.connected = True
                self.connection_id = conn_handle

        observer = ConnectionObserver()

        self._adapter.driver.observer_register(observer)
        self._adapter.connect(BLEGapAddr(BLEGapAddr.Types.random_static, NrfBackend.mac_string_to_bin(mac)))

        while not observer.connected:
            pass

        self._connection = observer.connection_id

        sleep(2)
        self._adapter.service_discovery(self._connection)
        sleep(2)
        self._adapter.authenticate(self._connection, BLEGapRoles.central)

    def disconnect(self):
        """disconnect from a device.
        Only required by some backends"""
        self._adapter.disconnect(self._connection)

    @staticmethod
    def scan_for_devices(timeout, adapter) -> List[Tuple[str, str]]:
        """Scan for additional devices.
        Returns a list of all the mac addresses of ble devices found.
        """

        class ScanDriverObserver(BLEDriverObserver):

            def __init__(self):
                super(ScanDriverObserver, self).__init__()
                self.advertised_devices = []

            def on_gap_evt_adv_report(
                    self, ble_driver, conn_handle, peer_addr, rssi, adv_type, adv_data
            ):
                if BLEAdvData.Types.complete_local_name in adv_data.records:
                    dev_name_list = adv_data.records[BLEAdvData.Types.complete_local_name]

                elif BLEAdvData.Types.short_local_name in adv_data.records:
                    dev_name_list = adv_data.records[BLEAdvData.Types.short_local_name]

                else:
                    return

                dev_name = "".join(chr(e) for e in dev_name_list)
                dev_addr = NrfBackend.mac_bin_to_string(peer_addr.addr)
                self.advertised_devices.append((dev_name, dev_addr))

        observer = ScanDriverObserver()

        driver = BLEDriver(serial_port=adapter, auto_flash=False, baud_rate=1000000, log_severity_level="debug")
        driver.open()
        driver.ble_enable()
        driver.observer_register(observer)
        driver.ble_gap_scan_start(scan_params=BLEGapScanParams(interval_ms=200, window_ms=150, timeout_s=timeout))
        sleep(timeout)
        driver.close()

        return list(set(observer.advertised_devices))


devices = NrfBackend.scan_for_devices(10, "COM5")
for name, mac in devices:
    print(name + mac)

classInstance = NrfBackend("COM5")
classInstance.connect("DA:D8:01:88:59:07")
