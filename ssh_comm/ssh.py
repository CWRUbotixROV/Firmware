import paramiko
from paramiko import SSHClient

class SSH_Config():

    def __init__(self, ip, user, password):
        self.ip = ip
        self.user = user
        self.password = password

class SSH(SSHClient):
    """Class to represent an SSH connection to the Raspberry Pi."""
    COMPANION = SSH_Config('192.168.2.2', 'pi', 'companion')
    ZERO      = SSH_Config('192.168.3.2', 'pi', 'raspberry')

    def __init__(self, config, sock=None):
        """Create a new SSH object."""
        super(SSH, self).__init__()
        # don't really need security for this SSH connection since its over local
        self.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # make the connection
        if sock is None:    # use default if no socket was provided
            self.connect(config.ip, username=config.user, password=config.password)
        else:               # Use the socket provided via the constructor
            self.connect(config.ip, username=config.user, password=config.password, sock=sock)

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

