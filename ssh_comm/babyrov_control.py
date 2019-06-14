#import pigpio  # this might be the wrong import
import argparse
import struct
import time

ARGS_WINCH_SPEED_IDX    = 0
ARGS_THRUSTER_SPEED_IDX = 1

class Winch():
    """Class to control the winch on the main ROV."""

    PWM_OFF = 0

    ENABLE_PIN        = 12 # Channel 0 GPIO 12 has hardware timed PWM
    MOTOR_INPUT_PIN_1 = 23
    MOTOR_INPUT_PIN_2 = 24

    def unreel(self, speed):
        """Unreels the winch.

        :param int speed: a PWM value in the range [0-255] that defines the speed to unreel

        """
        self.gpio.set_PWM_dutycycle(self.ENABLE_PIN, speed)

        self.gpio.write(self.MOTOR_INPUT_PIN_1, 1)
        self.gpio.write(self.MOTOR_INPUT_PIN_2, 0)

    def reel_in(self, speed):
        """Reels in the winch.

        :param int speed: a PWM value in the range [0-255] that defines the speed to reel in

        """
        self.gpio.set_PWM_dutycycle(self.ENABLE_PIN, speed)

        self.gpio.write(self.MOTOR_INPUT_PIN_1, 0)
        self.gpio.write(self.MOTOR_INPUT_PIN_2, 1)

    def stop(self):
        """Stops moving the winch."""
        self.gpio.set_PWM_dutycycle(self.ENABLE_PIN, self.PWM_OFF)

        self.gpio.write(self.MOTOR_INPUT_PIN_1, 0)
        self.gpio.write(self.MOTOR_INPUT_PIN_2, 0)

    def __init__(self):
        self.gpio = pigpio.pi()

        # put the digital pins into output mode
        self.gpio.set_mode(self.MOTOR_INPUT_PIN_1, pigpio.OUTPUT)
        self.gpio.set_mode(self.MOTOR_INPUT_PIN_2, pigpio.OUTPUT)

class Thruster():
    """Class to send serial messages to the BabyROV to control the Thruster."""
    THRUSTER_SPEED_OFF = 0

    def __init__(self):
        self.serial_conn = serial.Serial('/dev/ttyUSB0', 9600) # TODO: verify this port is correct

    def forward(self, speed):
        """Starts the thruster on BabyROV.

        :param byte speed: a value in the range [0-255] that specifies the speed of the thruster

        """
        self.serial_conn.write(bytes(speed))

    def stop(self):
        """Stops the thruster on the BabyROV."""
        self.serial_conn.write(bytes(self.THRUSTER_SPEED_OFF))


class BabyROV():
    """Class to enable moving the Baby ROV."""

    def __init__(self):
        self.winch = Winch()
        self.thruster = Thruster()

    def stop(self):
        """Stops the winch and stops the thruster"""
        winch.stop()
        thruster.stop()

    def forward(self, winch_speed, thruster_speed):
        """Moves the BabyROV forward and unreels the winch.

        :param int winch_speed:    a PWM value in the range [0-255] that defines
                                   the speed to unreel
        :param int thruster_speed: a PWM value int he range [0-255] that defines
                                   the speed for the thruster
        """
        winch.unreel(winch_speed)

        thruster.forward(thruster_speed)

    def backward(self, winch_speed):
        """Stops moving the BabyROV and reels in the winch.

        :param int winch_speed:    a PWM value in the range [0-255] that defines
                                   the speed to reel in
        """
        # stop the BabyROV from moving while it gets reeled in
        thruster.stop()

        winch.reel_in(winch_speed)


def parse_cmd_args():
    """Parses the command line args for setup and read options."""
    parser = argparse.ArgumentParser(description='Choose pH reading mode (Setup and/or Read)')

    parser.add_argument('--forward',
                        type=int,
                        nargs=2,
                        help='Moves the BabyROV forward and unreels the winch')
    parser.add_argument('--backward',
                        type=int,
                        nargs=1,
                        help='Stops moving the BabyROV and reels in the winch')
    parser.add_argument('--stop',
                        action='store_true',
                        help='Stops moving the BabyROV and stops the winch')

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_cmd_args()

    rov = BabyROV()

    # check the commands passed in via command line for what function to call
    if args.forward:
        rov.forward(args.forward[ARGS_WINCH_SPEED_IDX], args.forward[ARGS_THRUSTER_SPEED_IDX])
    elif args.backward:
        rov.backward(args.backward[ARGS_WINCH_SPEED_IDX])
    else:
        rov.stop()
