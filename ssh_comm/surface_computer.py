from tkinter import * #imports everything from the tkinter library
import time
import random
import serial
from ssh import SSH
from marker_dropper import MarkerDropper
from functools import partial
from marker_dropper import cmd_set_servo_angle

"""See documentation/Surface_Computer.md for more information on this script"""

class SettableText(Text):
    """Extends the tkinter Text object to allow the text to be changed."""

    def set_text(self, newtext):
        """Set the text in the text object to the new text.

        :param str newtext: the text to set the Text object to hold

        """
        # remove all the old text
        self.delete(1.0, END)

        # add the new text
        self.insert(END, newtext)


class ThrusterControl():
    """Class to represent and configure a thruster on the BabyROV."""

    NO_CONNECTION = 'No Connection'
    DESC = 'Thruster'
    FORWARD = '{DESC}: Forward'
    BACKWARD = '{DESC}: Backward'
    OFF = '{DESC}: Off'

    def __init__(self, ssh, text_output, speed, winch_forward_speed, winch_backward_speed):
        """Create a new ThrusterControl object

        :param string name:     an arbitrary name for the thruster
        :param obj ssh:         an SSH object to send commands to the Pi over
        :param obj text_output: a SettableText object that output is printed to

        """
        self.forward = False
        self.backward = False

        if ssh is not None:
            self.ssh = ssh
            self.FORWARD.format(DESC=self.DESC)
            self.BACKWARD.format(DESC=self.DESC)
        else:
            self.ssh = None
            self.FORWARD.format(DESC=self.NO_CONNECTION)
            self.BACKWARD.format(DESC=self.NO_CONNECTION)
            print("Thruster has no connection")

        self.text_output = text_output
        self.speed_text = speed
        self.winch_forward_speed_text = winch_forward_speed
        self.winch_backward_speed_text = winch_backward_speed
        self.thruster_forward_off()
        self.thruster_backward_off()

    def baby_forward(self):
        """
        Starts the baby ROV going forward on a time delay.
        """
        if self.ssh is not None:
            self.ssh.exec_command('python babyrov_control.py --timed')

    def thruster_forward(self, event=None):
        """Sends the command to move forward and updates the GUI.

        Note that the thruster on command is only sent if the thruster is not already on.

        :param obj event: obj with the event information that called this function

        """
        if not self.forward and not self.backward:
            self.text_output.set_text(self.FORWARD.format(DESC=self.DESC))
            # speed = self.speed_text.get('1.0', END)
            speed = 255
            # winch_speed = self.winch_forward_speed_text.get('1.0', END)
            winch_speed = 255
            if self.ssh is not None:
                self.ssh.exec_and_print('python babyrov_control.py --forward {} {}'.format(winch_speed, speed))
            self.forward = True

    def thruster_backward(self, event=None):
        """Sends the command to move backward and updates the GUI.

        Note that the thruster on command is only sent if the thruster is not already on.

        :param obj event: obj with the event information that called this function

        """
        if not self.forward and not self.backward:
            self.text_output.set_text(self.BACKWARD.format(DESC=self.DESC))
            speed = self.speed_text.get('1.0', END)
            # winch_speed = self.winch_backward_speed_text.get('1.0', END)
            winch_speed = 255
            if self.ssh is not None:
                self.ssh.exec_and_print('python babyrov_control.py --backward {}'.format(winch_speed))
            self.backward = True

    def thruster_forward_off(self, event=None):
        """Sends the command to the thruster to stop going forward and updates the GUI.

        :param obj event: obj with the event information that called this function

        """

        #self.ssh.exec_command('gpio write 4 0')
        self.forward = False

        if not self.backward:
            self.text_output.set_text(self.OFF.format(DESC=self.DESC))
            if self.ssh is not None:
                self.ssh.exec_and_print('python babyrov_control.py --forward 0 0')
        else:
            self.thruster_backward()


    def thruster_backward_off(self, event=None):
        """Sends the command to the thruster to stop going backward and updates the GUI.

        :param obj event: obj with the event information that called this function

        """
        self.backward = False

        if not self.forward:
            self.text_output.set_text(self.OFF.format(DESC=self.DESC))
            if self.ssh is not None:
                self.ssh.exec_and_print('python babyrov_control.py --backward 0')
        else:
            self.thruster_forward()

class ControlWindow():
    """Class to represent store all info for the GUI used to control the robot."""
    THRUSTER_BACKWARD_KEY = 's'
    THRUSTER_FORWARD_KEY = 'w'
    TEMP_SENSOR_KEY = 't'
    PH_SENSOR_KEY = 'p'
    SMART_HOOK_ACTUATOR = 'a'
    JUMBO_HOOK_ACTUATOR = 'd'
    DROP_RED_KEY = 'r'
    DROP_BLACK_KEY = 'b'

    NO_CONNECTION = 'No Connection: \n{READING}'
    ERROR = 'Error in Setup:\n{READING}'
    TEMP_TEXT = 'Last Temperature\nReading: {READING}'
    PH_TEXT = 'Last pH Reading: \n{READING}'
    SMART_TEXT = 'Smart hook state: \n{READING}'
    JUMBO_TEXT = 'Jumbo hook state: \n{READING}'
    READ_PENDING = 'Reading...'
    NO_READING = 'N/A'
    HOOK_ON = 'On'
    HOOK_OFF = 'Off'

    # Widths
    WINDOW_WIDTH       = 60
    HALF_WINDOW_WIDTH  = 30
    THIRD_WINDOW_WIDTH = 20

    # Heights
    INFO_BOX_HEIGHT             = 11
    THRUSTER_SPEED_HEIGHT       = 1
    WINCH_FORWARD_SPEED_HEIGHT  = 1
    WINCH_BACKWARD_SPEED_HEIGHT = 1
    THRUSTER_STATUS_HEIGHT      = 1
    SENSOR_READING_HEIGHT       = 2
    HOOK_STATUS_HEIGHT          = 2
    TOTAL_WINDOW_HEIGHT         = 18

    # Rows
    NUM_ROWS                 = 7
    INSTRUCTIONS_ROW         = 0
    THRUSTER_SPEED_ROW       = 1
    WINCH_FORWARD_SPEED_ROW  = 2
    WINCH_BACKWARD_SPEED_ROW = 3
    THRUSTERS_ROW            = 4
    SENSOR_ROW               = 5
    HOOK_ROW                 = 6

    # Columns
    NUM_COLUMNS      = 2
    INSTRUCTIONS_COL = 0
    SPEED_DESC_COL   = 0
    SPEED_COL        = 1
    THRUSTERS_COL    = 0
    TEMP_SENSOR_COL  = 0
    PH_SENSOR_COL    = 1
    SMART_HOOK_COL   = 0
    JUMBO_HOOK_COL   = 1


    def __init__(self, use_zero=False, red=[-2, -1], black=[1, 2]):
        # attempt to connect to the Companion computer.
        try:
            self.ssh = SSH(SSH.COMPANION)

            self.markerdropper = MarkerDropper(200, spacing=40, red_markers=red, black_markers=black, pin=18)
            self.ssh.exec_and_print(self.markerdropper.go_to_start())
        # if no connection can be made, make a note of that on the GUI
        except:
            self.TEMP_TEXT = self.NO_CONNECTION
            self.PH_TEXT = self.NO_CONNECTION
            self.ssh = None

        # attempt to connect to the arduino serial port
        ''' uncomment this and tab over the below code into the except once the relays are set up
        try:
            self.serial_conn = serial.Serial('COM13', 9600) # change this COM port with whatever comes up when plugged in
        # if no connection can be made, update the GUI to reflect that
        except:
        '''
        self.SMART_TEXT = self.NO_CONNECTION
        self.JUMBO_TEXT = self.NO_CONNECTION
        self.serial_conn = None


        self.smart_hook_state = self.HOOK_OFF
        self.jumbo_hook_state = self.HOOK_OFF

        self.master = Tk()

        self._add_instructions()
        self._setup_thrusters()
        self._setup_sensors()
        self._setup_hooks()

        self._bind_keys()

        self.master.mainloop()

    def jiggle_dropper(self):
        """
        Jiggle the marker dropper back and forth to release the marker.
        """
        left_cmd = cmd_set_servo_angle(self.markerdropper.angle-10, ang_range=self.markerdropper.ang_range)
        right_cmd = cmd_set_servo_angle(self.markerdropper.angle+10, ang_range=self.markerdropper.ang_range)
        home_cmd = cmd_set_servo_angle(self.markerdropper.angle, self.markerdropper.ang_range)
        for i in range(2):
            self.ssh.exec_and_print(left_cmd)
            time.sleep(0.5)
            self.ssh.exec_and_print(right_cmd)
            time.sleep(0.5)
        self.ssh.exec_and_print(home_cmd)

    def _add_instructions(self):
        """Adds the instruction text box to the GUI."""
        instructions = Text(self.master, height=self.INFO_BOX_HEIGHT, width=self.WINDOW_WIDTH)

        instructions.insert(END, 'Baby ROV Control:\n'
                                 'Press <{}> to move forward\n'
                                 'Press <{}> to move backward\n'
                                 '\nSensor Readings\n'
                                 'Press <{}> to get a temperature reading\n'
                                 'Press <{}> to get a pH reading.\n'
                                 'Press <{}> to toggle the smart hook actuator\n'
                                 'Press <{}> to toggle the jumbo hook actuator\n'
                                 'Press <{}> to drop a red marker.\n'
                                 'Press <{}> to drop a black marker.\n'
                                 ''.format(self.THRUSTER_FORWARD_KEY,
                                           self.THRUSTER_BACKWARD_KEY,
                                           self.TEMP_SENSOR_KEY,
                                           self.PH_SENSOR_KEY,
                                           self.SMART_HOOK_ACTUATOR,
                                           self.JUMBO_HOOK_ACTUATOR,
                                           self.DROP_RED_KEY,
                                           self.DROP_BLACK_KEY))

        # place the instruction at the top of the GUI window
        instructions.grid(row=self.INSTRUCTIONS_ROW,
                          column=self.INSTRUCTIONS_COL,
                          columnspan=self.NUM_COLUMNS)
        instructions.grid()

        instructions.config(state='disabled')

    def _setup_thrusters(self):
        """Adds the thruster info boxes to the GUI."""

        # setup the thruster speed input description under the instructions
        self.thruster_speed_desc = Text(self.master, height=self.THRUSTER_SPEED_HEIGHT, width=self.HALF_WINDOW_WIDTH)
        self.thruster_speed_desc.grid(row=self.THRUSTER_SPEED_ROW, column=self.SPEED_DESC_COL)
        self.thruster_speed_desc.insert(END, 'Thruster Speed:')
        self.thruster_speed_desc.config(state='disabled')

        # setup the winch forward speed input description under the thruster speed
        self.winch_forward_speed_desc = Text(self.master, height=self.WINCH_FORWARD_SPEED_HEIGHT, width=self.HALF_WINDOW_WIDTH)
        self.winch_forward_speed_desc.grid(row=self.WINCH_FORWARD_SPEED_ROW, column=self.SPEED_DESC_COL)
        self.winch_forward_speed_desc.insert(END, 'Winch Forward Speed:')
        self.winch_forward_speed_desc.config(state='disabled')

        # setup the winch backward speed input description under the winch forward
        self.winch_backward_speed_desc = Text(self.master, height=self.WINCH_BACKWARD_SPEED_HEIGHT, width=self.HALF_WINDOW_WIDTH)
        self.winch_backward_speed_desc.grid(row=self.WINCH_BACKWARD_SPEED_ROW, column=self.SPEED_DESC_COL)
        self.winch_backward_speed_desc.insert(END, 'Winch Backward Speed:')
        self.winch_backward_speed_desc.config(state='disabled')

        # setup the thruster speed input box
        self.thruster_speed = Text(self.master, height=self.THRUSTER_SPEED_HEIGHT, width=self.HALF_WINDOW_WIDTH)
        self.thruster_speed.grid(row=self.THRUSTER_SPEED_ROW, column=self.SPEED_COL)
        self.thruster_speed.insert(END, '0')

        # setup the winch forward speed input box
        self.winch_forward_speed = Text(self.master, height=self.WINCH_FORWARD_SPEED_HEIGHT, width=self.HALF_WINDOW_WIDTH)
        self.winch_forward_speed.grid(row=self.WINCH_FORWARD_SPEED_ROW, column=self.SPEED_COL)
        self.winch_forward_speed.insert(END, '0')

        # setup the winch backward speed input box
        self.winch_backward_speed = Text(self.master, height=self.WINCH_BACKWARD_SPEED_HEIGHT, width=self.HALF_WINDOW_WIDTH)
        self.winch_backward_speed.grid(row=self.WINCH_BACKWARD_SPEED_ROW, column=self.SPEED_COL)
        self.winch_backward_speed.insert(END, '0')

        # create text box for left thruster on left under the speed input boxes
        self.thruster_state = SettableText(self.master,
                                           height=self.THRUSTER_STATUS_HEIGHT,
                                           width=self.WINDOW_WIDTH)
        self.thruster_state.grid(row=self.THRUSTERS_ROW, column=self.THRUSTERS_COL,  columnspan=self.NUM_COLUMNS)

        # create control object for left thruster
        self.thruster = ThrusterControl(self.ssh,
                                        self.thruster_state,
                                        self.thruster_speed,
                                        self.winch_forward_speed,
                                        self.winch_backward_speed)

    def _setup_sensors(self):
        """Adds the pH and temperature info boxes to the GUI."""
        # create the text box for pH reading under the left thruster
        self.ph_reading = SettableText(self.master,
                                       height=self.SENSOR_READING_HEIGHT,
                                       width=self.HALF_WINDOW_WIDTH)
        self.ph_reading.grid(row=self.SENSOR_ROW, column=self.PH_SENSOR_COL)

        # send the setup commands to the pH sensor
        if self.ssh is not None:
            result = self.ssh.exec_and_print('python ph_sensor.py --setup')

            # if the setup commands failed, update what the GUI displays
            if 'Success' not in result:
                self.PH_TEXT = self.ERROR

        self.ph_reading.set_text(self.PH_TEXT.format(READING=self.NO_READING))

        # create the text box for temperature reading under the right thruster
        self.temp_reading = SettableText(self.master,
                                         height=self.SENSOR_READING_HEIGHT,
                                         width=self.HALF_WINDOW_WIDTH)
        self.temp_reading.grid(row=self.SENSOR_ROW, column=self.TEMP_SENSOR_COL)
        self.temp_reading.set_text(self.TEMP_TEXT.format(READING=self.NO_READING))

    def _setup_hooks(self):
        """Adds the hook status boxes to the GUI."""
        # create the text box for pH reading under the left thruster
        self.smart_hook = SettableText(self.master,
                                       height=self.HOOK_STATUS_HEIGHT,
                                       width=self.HALF_WINDOW_WIDTH)
        self.smart_hook.grid(row=self.HOOK_ROW, column=self.SMART_HOOK_COL)
        self.smart_hook.set_text(self.SMART_TEXT.format(READING=self.HOOK_OFF))

        # create the text box for temperature reading under the right thruster
        self.jumbo_hook = SettableText(self.master,
                                         height=self.HOOK_STATUS_HEIGHT,
                                         width=self.HALF_WINDOW_WIDTH)
        self.jumbo_hook.grid(row=self.HOOK_ROW, column=self.JUMBO_HOOK_COL)
        self.jumbo_hook.set_text(self.JUMBO_TEXT.format(READING=self.HOOK_OFF))

    def _bind_keys(self):
        """Bind the keys for the peripherals (ie thrusters, sensors, etc)."""
        # bind the right thruster key to turn it on and off
        self.master.bind('<KeyPress-{}>'.format(self.THRUSTER_FORWARD_KEY),
                         self.thruster.thruster_forward)
        self.master.bind('<KeyPress-{}>'.format(self.THRUSTER_BACKWARD_KEY),
                        self.thruster.thruster_backward_off)

        # bind the left thruster key to turn it on and off
        self.master.bind('<KeyPress-{}>'.format(self.THRUSTER_BACKWARD_KEY),
                         self.thruster.thruster_backward)
        self.master.bind('<KeyRelease-{}>'.format(self.THRUSTER_BACKWARD_KEY),
                         self.thruster.thruster_backward_off)

        # bind the temperature sensor key
        self.master.bind('<KeyPress-{}>'.format(self.TEMP_SENSOR_KEY),
                         self.read_temp_sensor)

        # bind the pH sensor key
        self.master.bind('<KeyPress-{}>'.format(self.PH_SENSOR_KEY),
                         self.read_ph_sensor)

        # bind the keys to drop red and black markers, using a partial function to repeat less code
        self.master.bind(f'<KeyPress-{self.DROP_RED_KEY}>', partial(self.drop_marker, red=True))
        self.master.bind(f'<KeyPress-{self.DROP_BLACK_KEY}>', partial(self.drop_marker, red=False))

        # bind smart hook actuator
        self.master.bind('<KeyPress-{}>'.format(self.SMART_HOOK_ACTUATOR),
                         self.toggle_smart_hook)

        # bind jumbo hook actuator
        self.master.bind('<KeyPress-{}>'.format(self.JUMBO_HOOK_ACTUATOR),
                         self.toggle_jumbo_hook)

    def read_temp_sensor(self, event=None):
        """Sends the SSH command to read the temperature sensor and updates its info box.

        : param obj event: obj with the event information that called this function

        """
        # change the text box to indicate that the temperature is being read
        self.temp_reading.set_text(self.TEMP_TEXT.format(READING=self.READ_PENDING))

        # send the read command
        reading = self.ssh.exec_and_print('python ~/temp_reading.py')
        #reading = random.randint(1, 14)

        # update the GUI text box
        self.temp_reading.set_text(self.TEMP_TEXT.format(READING=reading))

    def read_ph_sensor(self, event=None):
        """Sends the SSH command to read the pH sensor and updates its info box.

        :param obj event: obj with the event information that called this function

        """
        # change the text box to indicate that the pH is being read
        self.ph_reading.set_text(self.PH_TEXT.format(READING=self.READ_PENDING))

        # send the read command
        reading = self.ssh.exec_and_print('python ph_sensor.py --read')

        # update the GUI text box
        self.ph_reading.set_text(self.PH_TEXT.format(READING=reading))

    def drop_marker(self, event=None, red=True):
        """
        Drops a marker.

        Arguments:
            red (bool): True if a red marker should be dropped, False if a black one should be dropped
        """
        if red:
            cmd, has_markers = self.markerdropper.drop_red_marker()
        else:
            cmd, has_markers = self.markerdropper.drop_black_marker()
        # print(cmd)
        if has_markers:
            print(cmd)
            self.ssh.exec_and_print(cmd)
            self.markerdropper.success()
            self.jiggle_dropper()
            home = self.markerdropper.go_to_start()
            print(home)
            time.sleep(1)
            self.ssh.exec_and_print(home)
            self.markerdropper.success()

    def toggle_smart_hook(self, event=None):
        """Sends the serial command to toggle the smart hook and update its status box.

        :param obj event: obj with the event information that called this function

        """
        # send the command to toggle the smart hook
        self.serial_conn.write(bytes(self.SMART_HOOK_ACTUATOR, 'utf-8'))

        # toggle the GUI state
        if (self.smart_hook_state is self.HOOK_ON):
            self.smart_hook_state = self.HOOK_OFF
        else:
            self.smart_hook_state = self.HOOK_ON

        # reflect the new state on the GUI
        self.smart_hook.set_text(self.SMART_TEXT.format(READING=self.smart_hook_state))

    def toggle_jumbo_hook(self, event=None):
        """Sends the serial command to toggle the jumbo hook and update its status box.

        :param obj event: obj with the event information that called this function

        """
        # send the command to toggle the jumbo hook
        self.serial_conn.write(bytes(self.JUMBO_HOOK_ACTUATOR, 'utf-8'))

        # toggle the GUI state
        if (self.jumbo_hook_state is self.HOOK_ON):
            self.jumbo_hook_state = self.HOOK_OFF
        else:
            self.jumbo_hook_state = self.HOOK_ON

        # reflect the new state on the GUI
        self.jumbo_hook.set_text(self.JUMBO_TEXT.format(READING=self.jumbo_hook_state))

if __name__ == "__main__":
    x = ControlWindow()
