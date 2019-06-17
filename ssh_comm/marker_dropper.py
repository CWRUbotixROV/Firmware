"""Code to control the marker dropper."""

def cmd_set_servo_angle(angle, ang_range=270, pin=18):
    """
    Returns a pigs command to set the angle of a servo.

    Arguments:
        angle (float): the angle to set the servo to, in degrees
        ang_range (float): the angular range of the servo, in degrees
        pin (int): the GPIO pin for the servo
    """
    MIN_TIME = 500
    MAX_TIME = 2500
    time_range = MAX_TIME - MIN_TIME
    usec = int(MIN_TIME + (angle/ang_range)*time_range)  # calculte pulse duration in microseconds for angle
    return f"pigs s {pin} {usec}"


class MarkerDropper():
    """A class to represent the marker dropper on the ROV."""
    
    def __init__(self, ang_range=270, spacing=40, red_markers=[], black_markers=[], pin=18):
        """
        Initialize the MarkerDropper object.

        Arguments:
            ang_range (int): the range, in degrees, of the servo
            spacing (int): the spacing, in degrees, between adjacent markers
            red_markers : array of ints containing the positions (1-6) of red markers
            black_markers : array of ints containing the positions (1-6) of black markers
            pin (int): the GPIO pin for the servo that rotates the dropper
        """
        self.ang_range = ang_range
        self.spacing = spacing
        self.offset = ang_range/2
        self.angle = self.offset
        self.red_markers = red_markers
        self.black_markers = black_markers
        self.red_markers.sort()
        self.black_markers.sort()
        self.pin = pin

        self.tmp_angle = self.angle     # used so we only update the angle and marker arrays once the command succeeds
        self.last_dropped = 'red'

    def go_to_start(self):
        """
        Returns a command to rotate the mechanism to the starting position. Should be called once, before any markers
        are dropped. Alternatively, the mechanism can be positioned by hand, and this call can be omitted.
        """
        self.last_dropped = 'home'
        return cmd_set_servo_angle(self.offset, ang_range=self.ang_range, pin=self.pin)

    def drop_red_marker(self):
        """
        Generates the pigs command to drop a red marker if there are any left.

        Returns:
            string: a pigs command to rotate the servo
            bool: whether there were red markers left to drop
        """
        if len(self.red_markers) > 0:
            """If there are still red markers left, we return the pigs command to drop the next one and store
            what we just did. It will only update if the pigs command is successful."""
            self.tmp_angle = (self.red_markers[-1])*self.spacing + self.offset  # go from the end
            print(self.tmp_angle)
            self.last_dropped = 'red'
            return cmd_set_servo_angle(self.tmp_angle, ang_range=self.ang_range, pin=self.pin), True
        print("No more red markers!")
        return cmd_set_servo_angle(self.angle, ang_range=self.ang_range, pin=self.pin), False

    def drop_black_marker(self):
        """
        Generates the pigs command to drop a black marker if there are any left.

        Returns:
            string: a pigs command to rotate the servo
            bool: whether there were black markers left to drop
        """
        if len(self.black_markers) > 0:
            # Works exactly like drop_red_marker
            self.tmp_angle = (self.black_markers[0])*self.spacing + self.offset
            print(self.tmp_angle)
            self.last_dropped = 'black'
            return cmd_set_servo_angle(self.tmp_angle, ang_range=self.ang_range, pin=self.pin), True
        print("No more black markers!")
        return cmd_set_servo_angle(self.angle, ang_range=self.ang_range, pin=self.pin), False
    
    def success(self):
        """
        Update the state of this MarkerDropper object. Should be called if and only if the rotate command
        was successful.
        """
        self.angle = self.tmp_angle
        if self.last_dropped == 'red':
            self.red_markers = self.red_markers[:-1]
        if self.last_dropped == 'black':
            self.black_markers = self.black_markers[1:]

