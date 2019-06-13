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

    self.gpio.write(MOTOR_INPUT_PIN_1, 1) # <---- make this 0
    self.gpio.write(MOTOR_INPUT_PIN_2, 0) # <---- make this 1

def reel_in(self, speed):
    """Reels in the winch.

    :param int speed: a PWM value in the range [0-255] that defines the speed to reel in

    """
    self.gpio.set_PWM_dutycycle(self.ENABLE_PIN, speed)

    self.gpio.write(MOTOR_INPUT_PIN_1, 0) # <---- make this 1
    self.gpio.write(MOTOR_INPUT_PIN_2, 1) # <---- make this 0
```

