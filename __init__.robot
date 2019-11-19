*** Settings ***
Documentation    This is the initial setting before executing each test suite execution
Resource  ../../Resources/System_Common/EL_HybMan_Common_Keywords.robot
Suite Setup     Make setup
Suite Teardown      Close all Connection

*** Keywords ***
Establish Connection
  run keyword if  ${world}== "REAL"     _Establish Connection to real world
  run keyword if  ${world}== "SIMULATION"     _Establish Connection to simulation world

  load emspd file  ${emspd_path}
  load config file  ${sensor_file}

_Establish Connection to real world
    connect to ems  ${edo_com_port}
    connect to can   ${CanConfig_file}   gui= "yes"
    enable forced read for ems signals

_disconnect simulationdevices
    disconnect ems
    shutdown simulation system

_disconnect realdevices
     disconnect ems
     disconnect can

Make setup
    Establish Connection
    Hybman_System_Idle

Close all Connection
    run keyword if  ${world}== "REAL"   _disconnect realdevices
    run keyword if  ${world}== "SIMULATION"    _disconnect simulationdevices

Hybman_System_Idle


        HybMan : Initialize the System_Boiler data
        HybMan : Initialize the HC1 data
        HybMan : Initialize the HC2 data
        HybMan : Initiliaze the DHW1 data
        HybMan : Initiliaze the DHW2 data
        HybMan : SoftReset HybMan once before the startup
        HybMan: Generic wait for 10 sec duration
        #HybMan : Cancel all Low noise operations
        HybMan : Cancel all Heat requests
        HybMan : Cancel all DHW requests
        Appliance :Assert Appliance Outputs in Idle state
        HybMan : Assert HybMan outputs in idle state