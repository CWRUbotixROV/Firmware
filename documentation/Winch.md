# Winch

## Setup

1. Navigate to the `ssh_comm` folder in your terminal.
2. Power on the companion computer
3. Once the Pi is all booted up and you can ssh into it, execute `scp babyrov_control.py pi@192.168.2.2:~/`
    - This will copy the control script over to the Pi
4. Load the `babyrov_arduino.ino` file onto the BabyROV Arduino Nano via the Arduino IDE (or using whatever driver is necessary - I think Peter knew what this was)
5. Run `ssh_comm/surface_computer.py` in windows command prompt (WSL does not work since this uses TKinter).
    - If you run into any issues connecting to the Pi, follow the instructions in [Surface Computer](./Surface_Computer.md)
6. The GUI should now have three new text box rows
    1. Thruster Speed
    1. Winch Forward Speed
    1. Winch Backward Speed
7. The editable boxes on the right side of the rows are where you should put the values you want to use to move the BabyROV/winch
    - The values should all be in the range [0,255]
8. Pressing `w` and `s` will move the BabyROV/Winch forward and backward (respectively)

## General Usage of `babyrov_control.py`

This script accepts command line arguments (the GUI should handle all of this already, but if you find yourself needing to run the script manually, these are the commands.  Make sure to only use one at a time).

Usage:
```shell
python babyrov_control.py --<command> [arg1] [arg2]
```

|Command|Argument 1||Description|
|:--:|:--:|
|forward|
|backward|
|stop|
|help|
optional arguments:
  -h, --help            show this help message and exit
  --forward FORWARD FORWARD
                        Moves the BabyROV forward and unreels the winch
  --backward BACKWARD   Stops moving the BabyROV and reels in the winch
  --stop                Stops moving the BabyROV and stops the winch

## Troubleshooting

### Winch turns in the wrong direction

I was not sure about the values I was writing to the Winch in terms of direction.

`reel_in()` and `unreel()` control the direction. If you flip the 0's and 1's in the `ssh_comms/babyrov_control.py`, then everything should rotate in the opposite and correct direction if its wrong to start.

```python
def unreel(self, speed):
    """Unreels the winch.

    :param int speed: a PWM value in the range [0-255] that defines the speed to unreel

    """
    self.gpio.set_PWM_dutycycle(self.ENABLE_PIN, speed)

    self.gpio.write(MOTOR_INPUT_PIN_1, 1) # <---- make this 0 if it goes in the wrong direction
    self.gpio.write(MOTOR_INPUT_PIN_2, 0) # <---- make this 1 if it goes in the wrong direction

def reel_in(self, speed):
    """Reels in the winch.

    :param int speed: a PWM value in the range [0-255] that defines the speed to reel in

    """
    self.gpio.set_PWM_dutycycle(self.ENABLE_PIN, speed)

    self.gpio.write(MOTOR_INPUT_PIN_1, 0) # <---- make this 1 if it goes in the wrong direction
    self.gpio.write(MOTOR_INPUT_PIN_2, 1) # <---- make this 0 if it goes in the wrong direction
```

### Serial Connection

I am not 100% sure the connection to the Arduino Nano is going to work. I think that the serial port should be `/dev/ttyUSB0` or something like that.

The following code in the `ssh_comms/babyrov_control.py` file is what needs to be changed (the `'/dev/ttyUSB0'` is what should be changed - make sure to leave the quotes).

```python
class Thruster():
    """Class to send serial messages to the BabyROV to control the Thruster."""
    THRUSTER_SPEED_OFF = 0

    def __init__(self):
        self.serial_conn = serial.Serial('/dev/ttyUSB0', 9600) # TODO: verify this port is correct
```
