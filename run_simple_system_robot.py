import sys
import os
import runpy

#TEST_ROOT_DIRECTORY = "../.."
TEST_ROOT_DIRECTORY = "."

commandline_arguments = []
commandline_arguments.extend([
    "--argumentfile", 'robot_arguments.txt',
    '--consolecolors', 'ansi',
    '--consolewidth', '150',
    '--outputdir', 'results'
])
commandline_arguments.append(TEST_ROOT_DIRECTORY)
print("Appending commandline arguments: ")
sys.argv = [os.path.basename(__file__)]
sys.argv.extend(commandline_arguments)
print(' '.join(commandline_arguments))
print ("Starting python module called \"robot\"")
runpy.run_module("robot", alter_sys=True)
