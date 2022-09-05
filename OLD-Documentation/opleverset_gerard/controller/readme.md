# Sens2Sea Object-Tracking Camera

## Required programs and packages

The controller, user interface and all surrounding scripts are written in Python and require Python 3.x to run. (Everything was tested on version 3.9)

You can download the latest python version from [the official website](https://www.python.org/downloads/).

After installation, you will need to install certain packages that make the scripts function. All of them are listed in install/requirements.txt

The package versions from the packages in the requirements are the last tested version the system ran on. If you are not using a virtual environment for this project I recommend installing the latest version of these packages instead. If the program doesn't function then you can always revert the packages back to the tested version.

For the installation of the packages, you can use the included batch file that also checks if you correctly installed Python. Alternatively, you can use pip directly from your terminal to install the packages:

```bash
pip install -r ./install/requirements.txt
```

## Variables

All system variables can be changed in the .env file for the server and client respectively.

## Operation

To run the system 2 or 3 scripts need to be started depending on the situation

### Testing
For testing you will need to run 3 scripts in the following order to ensure everything works as expected:
```bash
radar_simulation.py found in the controller/simulation folder
controller.py found in the controller folder
user_interface.py found in the controller folder
```
The user interface doesn't need to be run and multiple user interfaces can run at the same time as each other from different machines or on the same machine.

### Production
During normal operation with a connected radar, the only script that needs to be running on the machine is the controller script. A user interface should be able to connect remotely to the controller when in operation.

## Notes

When the controller script is stopped or crashes with clients connected the user interface script will also crash. This crash will cause the different Threads to not behave as they should, this should be fixed soon but is a known issue in this version. To stop it you may have to resort to ending the process using the terminal or task manager on windows.

It is a known issue that the program raises errors upon closing the controller. These can be ignored for now as they originate from a crash prevention mechanism that is now obsolete and will be removed.