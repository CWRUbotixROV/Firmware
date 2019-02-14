from tkinter import * #imports everything from the tkinter library
import paramiko
from paramiko import SSHClient
import time
import random


class SettableText(Text):
    def set_text(self, newtext):
        self.delete(1.0, END)
        self.insert(END, newtext)

class SSH(SSHClient):
    """Class to represent an SSH connection to the Raspberry Pi."""

    def __init__(self):
        # don't really need security for this SSH connection since its over local
        self.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # make the connection
        self.connect('192.168.2.2', username='pi', password='companion')

        # setup the debugging GPIO TODO: remove this once debugging is done.
        self.exec_command('gpio mode 4 out')

    def exec_and_print(self, cmd):
        """Sends the command over the SSH connection and print the output to the console.

        :param str cmd: the command to send over ssh reppresented as a string
        :returns:       the string output from the command (also printed to console)

        """
        # send the command and store the stdout value
        out = self.exec_command(cmd)[1]

        # get the string stored in stdout and print
        out_string = out.read().decode('ascii').strip("\n")
        print(out_string)

        return out_string

class ThrusterControl():
    """Class to represent and configure a thruster on the BabyROV."""

    def __init__(self, name, ssh, text_output):
        """Create a new ThrusterControl object

        :param string name:     an arbitrary name for the thruster
        :param obj ssh:         an SSH object to send commands to the Pi over
        :param obj text_output: a SettableText object that output is printed to

        """
        self.on = False
        self.name = name

        self.text_output = text_output
        self.thruster_off()

        #self.ssh = ssh

    def thruster_on(self, event=None):
        """Sends the command to turn on the thruster and updates the GUI.

        Note that the thruster on command is only sent if the thruster is not already on.

        :param obj event: obj with the event information that called this function

        """
        if not self.on:
            self.text_output.set_text('{} Thruster On'.format(self.name))
            #self.ssh.exec_command('gpio write 4 1')
            #self.ssh.exec_and_print('echo hello')
            self.on = True

    def thruster_off(self, event=None):
        """Sends the command to turn off the thruster and updates the GUI.

        :param obj event: obj with the event information that called this function

        """
        self.text_output.set_text('{} Thruster Off'.format(self.name))
        #self.ssh.exec_command('gpio write 4 0')
        self.on = False

class ControlWindow():
    """Class to represent store all info for the GUI used to control the robot."""

    LEFT_THRUSTER_KEY = 'a'
    RIGHT_THRUSTER_KEY = 'd'
    TEMP_SENSOR_KEY = 't'
    PH_SENSOR_KEY = 'p'

    TEMP_TEXT = "Last Temperature\nReading: {READING}"
    PH_TEXT = "Last pH Reading: \n{READING}"

    def __init__(self):
        #self.ssh = SSH()

        self.master = Tk()

        self._add_instructions()
        self._setup_thrusters()
        self._setup_sensors()

        self._bind_keys()

        self.master.mainloop()

    def _add_instructions(self):
        instructions = Text(self.master, height=7, width=40)
        #instructions.pack()

        instructions.insert(END, 'Baby ROV Control:\n'
                                 'Press <{}> to power the left thruster\n'
                                 'Press <{}> to power the right thruster\n'
                                 '\nSensor Readings\n'
                                 'Press <{}> to get a temperature reading\n'
                                 'Press <{}> to get a pH reading.\n'
                                 ''.format(self.LEFT_THRUSTER_KEY,
                                           self.RIGHT_THRUSTER_KEY,
                                           self.TEMP_SENSOR_KEY,
                                           self.PH_SENSOR_KEY))

        instructions.grid(row=0, column=0, columnspan=2)
        instructions.grid()

    def _setup_thrusters(self):
        # create text box for left thruster on left under the instructions
        self.left_thruster_state = SettableText(self.master, height=1, width=20)
        self.left_thruster_state.grid(row=1, column=0)

        # create control object for left thruster
        self.left_thruster = ThrusterControl('Left', None, self.left_thruster_state)

        # create text box for right thruster on the right of the left thruster text
        self.right_thruster_state = SettableText(self.master, height=1, width=20)
        self.right_thruster_state.grid(row=1, column=1)

        # create control object for right thruster
        self.right_thruster = ThrusterControl('Right', None, self.right_thruster_state)

    def _setup_sensors(self):
        # create the text box for pH reading under the left thruster
        self.ph_reading = SettableText(self.master, height=2, width=20)
        self.ph_reading.grid(row=2, column=0)
        self.ph_reading.set_text(self.PH_TEXT.format(READING='N/A'))

        # create the text box for temperature reading under the right thruster
        self.temp_reading = SettableText(self.master, height=2, width=20)
        self.temp_reading.grid(row=2, column=1)
        self.temp_reading.set_text(self.TEMP_TEXT.format(READING='N/A'))

    def _bind_keys(self):
        # bind the right thruster key to turn it on and off
        self.master.bind('<KeyPress-{}>'.format(self.RIGHT_THRUSTER_KEY),
                         self.right_thruster.thruster_on)
        self.master.bind('<KeyRelease-{}>'.format(self.RIGHT_THRUSTER_KEY),
                         self.right_thruster.thruster_off)

        # bind the left thruster key to turn it on and off
        self.master.bind('<KeyPress-{}>'.format(self.LEFT_THRUSTER_KEY),
                         self.left_thruster.thruster_on)
        self.master.bind('<KeyRelease-{}>'.format(self.LEFT_THRUSTER_KEY),
                         self.left_thruster.thruster_off)

        # bind the temperature sensor key
        self.master.bind('<KeyPress-{}>'.format(self.TEMP_SENSOR_KEY),
                         self.read_temp_sensor)

        # bind the pH sensor key
        self.master.bind('<KeyPress-{}>'.format(self.PH_SENSOR_KEY),
                         self.read_ph_sensor)

    def read_temp_sensor(self, event=None):
        # send the read command
        #reading = self.ssh.exec_and_print('echo \'TODO: read the temp sensor\'')
        reading = random.randint(1, 14)

        # update the GUI text box
        self.ph_reading.set_text(self.PH_TEXT.format(READING=reading))

    def read_ph_sensor(self, event=None):
        # send the read command
        #reading = self.ssh.exec_and_print('echo \'TODO: read the pH sensor\'')
        reading = random.randint(0, 100)

        # update the GUI text box
        self.temp_reading.set_text(self.TEMP_TEXT.format(READING=reading))

if __name__ == "__main__":
    x = ControlWindow()