from tkinter import * #imports everything from the tkinter library
import time
import random
import serial
from ssh import SSH

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

    def __init__(self, ssh, text_output):
        """Create a new ThrusterControl object

        :param string name:     an arbitrary name for the thruster
        :param obj ssh:         an SSH object to send commands to the Pi over
        :param obj text_output: a SettableText object that output is printed to

        """
        self.forward = False
        self.backward = False

        self.ssh = ssh

        if self.ssh is None:
            self.DESC = self.NO_CONNECTION

        self.text_output = text_output
        self.thruster_forward_off()
        self.thruster_backward_off()

    def thruster_forward(self, event=None):
        """Sends the command to move forward and updates the GUI.

        Note that the thruster on command is only sent if the thruster is not already on.

        :param obj event: obj with the event information that called this function

        """
        if not self.forward and not self.backward:
            self.text_output.set_text(self.FORWARD.format(DESC=self.DESC))
            self.forward = True

    def thruster_backward(self, event=None):
        """Sends the command to move backward and updates the GUI.

        Note that the thruster on command is only sent if the thruster is not already on.

        :param obj event: obj with the event information that called this function

        """
        if not self.forward and not self.backward:
            self.text_output.set_text(self.BACKWARD.format(DESC=self.DESC))
            self.backward = True

    def thruster_forward_off(self, event=None):
        """Sends the command to the thruster to stop going forward and updates the GUI.

        :param obj event: obj with the event information that called this function

        """

        #self.ssh.exec_command('gpio write 4 0')
        self.forward = False

        if not self.backward:
            self.text_output.set_text(self.OFF.format(DESC=self.DESC))
        else:
            self.thruster_backward()


    def thruster_backward_off(self, event=None):
        """Sends the command to the thruster to stop going backward and updates the GUI.

        :param obj event: obj with the event information that called this function

        """
        self.backward = False

        if not self.forward:
            self.text_output.set_text(self.OFF.format(DESC=self.DESC))
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
    WINDOW_WIDTH      = 40
    HALF_WINDOW_WIDTH = 20

    # Heights
    THRUSTER_STATUS_HEIGHT = 1
    SENSOR_READING_HEIGHT  = 2
    HOOK_STATUS_HEIGHT     = 2
    TOTAL_WINDOW_HEIGHT    = 12

    # Rows
    NUM_ROWS         = 3
    INSTRUCTIONS_ROW = 0
    THRUSTERS_ROW    = 1
    SENSOR_ROW       = 2
    HOOK_ROW         = 3

    # Columns
    NUM_COLUMNS      = 2
    INSTRUCTIONS_COL = 0
    THRUSTERS_COL    = 0
    TEMP_SENSOR_COL  = 0
    PH_SENSOR_COL    = 1
    SMART_HOOK_COL   = 0
    JUMBO_HOOK_COL   = 1


    def __init__(self):
        # attempt to connect to the Companion computer.
        try:
            self.ssh = SSH(SSH.COMPANION)
        # if no connection can be made, make a note of that on the GUI
        except:
            self.TEMP_TEXT = self.NO_CONNECTION
            self.PH_TEXT = self.NO_CONNECTION
            self.ssh = None

        # attempt to connect to the Pi Zero
        '''Uncomment once we actually have a BabyRov
        try:
            transport = self.ssh.get_transport()
            zero_addr = (SSH.ZERO.ip, 22)             # the address and port of the Pi Zero, as seen by the Pi 3
            companion_addr = (SSH.COMPANION, 22)      # the address and port of the Pi 3, as seen by the surface computer
            channel = transport.open_channel('direct-tcpip', zero_addr, companion_addr)
            self.zero_ssh = SSH(SSH.ZERO, sock=channel)
        # if no connection can be made, print to the console no connection was made
        except:
            print('No connection to thruster')
            self.zero_ssh=None
        '''
        self.zero_ssh=None  # remove this when above code gets uncommented

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

    def _add_instructions(self):
        """Adds the instruction text box to the GUI."""
        instructions = Text(self.master, height=self.TOTAL_WINDOW_HEIGHT, width=self.WINDOW_WIDTH)

        instructions.insert(END, 'Baby ROV Control:\n'
                                 'Press <{}> to move forward\n'
                                 'Press <{}> to move backward\n'
                                 '\nSensor Readings\n'
                                 'Press <{}> to get a temperature reading\n'
                                 'Press <{}> to get a pH reading.\n'
                                 'Press <{}> to toggle the smart hook actuator\n'
                                 'Press <{}> to toggle the jumbo hook actuator\n'
                                 ''.format(self.THRUSTER_FORWARD_KEY,
                                           self.THRUSTER_BACKWARD_KEY,
                                           self.TEMP_SENSOR_KEY,
                                           self.PH_SENSOR_KEY,
                                           self.SMART_HOOK_ACTUATOR,
                                           self.JUMBO_HOOK_ACTUATOR))

        # place the instruction at the top of the GUI window
        instructions.grid(row=self.INSTRUCTIONS_ROW,
                          column=self.INSTRUCTIONS_COL,
                          columnspan=self.NUM_COLUMNS)
        instructions.grid()

        instructions.config(state='disabled')

    def _setup_thrusters(self):
        """Adds the thruster info boxes to the GUI."""
        # create text box for left thruster on left under the instructions
        self.thruster_state = SettableText(self.master,
                                           height=self.THRUSTER_STATUS_HEIGHT,
                                           width=self.WINDOW_WIDTH)
        self.thruster_state.grid(row=self.THRUSTERS_ROW, column=self.THRUSTERS_COL,  columnspan=self.NUM_COLUMNS)

        # create control object for left thruster
        self.thruster = ThrusterControl(None, self.thruster_state)

    def _setup_sensors(self):
        """Adds the pH and temperature info boxes to the GUI."""
        # create the text box for pH reading under the left thruster
        self.ph_reading = SettableText(self.master,
                                       height=self.SENSOR_READING_HEIGHT,
                                       width=self.HALF_WINDOW_WIDTH)
        self.ph_reading.grid(row=self.SENSOR_ROW, column=self.PH_SENSOR_COL)

        '''uncomment once ph sensor reading is working
        # send the setup commands to the pH sensor
        if self.ssh is not None:
            result = self.ssh.exec_and_print('python ph_sensor.py --setup')

            # if the setup commands failed, update what the GUI displays
            if 'Success' not in result:
                self.PH_TEXT = self.ERROR
        '''

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
        self.master.bind('<KeyRelease-{}>'.format(self.THRUSTER_FORWARD_KEY),
                         self.thruster.thruster_forward_off)

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
