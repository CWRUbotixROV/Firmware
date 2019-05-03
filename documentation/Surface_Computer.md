# Surface Computer

In the `ssh_comm` folder of this repository, you can run the `surface_computer.py` script to connect to the robot.

## Setup

1. Connect the companion to the surface computer via ethernet.
1. Set up the surface computer to have a static IP of `192.168.2.1` (follow the Ardusub Network Setup guide [here](https://www.ardusub.com/getting-started/installation.html#raspberry-pi))
    - Note that the Pi Zero should be connected to the Pi 3 (the companion computer) via USB.
1. Make sure the companion computer has the latest versions of `temp_reading.py` and `ph_reading.py` in its home directory.
1. Connect the Arduino to the surface computer via USB and load the Arduino code in the `pneumatics_arduino` folder onto the arduino via the Arduino IDE.
1. Verify that the COM port used in `surface_computer.py` matches that of the Arduino.  If it does not, update it in `surface_computer.py` script
1. Everything should be setup at this point, so just run `surface_computer.py` and it should pull up a GUI (note that wherever you run the script from needs to be able to open a GUI so Windows Subsystem For Linux will not work)

## Notes

### pH Sensor
This sends setup commands to the ADC when the GUI starts up if an SSH connection was made to the companion computer.  This will put the pH sensor in the proper modes (continuous conversion and data ready mode) so that each reading gets the latest result stored on the ADC.  There will probably be a few seconds (or less - not sure how long) after sending those commands that the pH readings may be garbage / innacurate.  afterwards, pressing the pH reading key should put the read value into the GUI box.

Note that this code still needs to be tested - specifically I do not think the reading I am getting in the PHSensor class of ph_sensor.py is actually a floating point number, rather it is the raw bytes which needs to be converted, but I wont be able to verify that until I test.
