import pigpio  # this might be the wrong import
import argparse
import struct
import time

class PHSensor:
    """Class to handle communication with the ADC that reads the pH sensor."""
    # spi flags
    # 21 20 19 18 17 16 15 14 13 12 11 10  9  8  7  6  5  4  3  2  1  0
    #  b  b  b  b  b  b  R  T  n  n  n  n  W  A u2 u1 u0 p2 p1 p0  m  m
    #  0  0  0  0  0  0  1  0  0  0  0  0  0  0  0  0  0  0  0  0  0  1

    # m is the mode which is 1
    # p is 0 since CS is active low
    # u is 0 since using GPIO reserved for SPI
    # A is 0 since using main SPI
    # W is 0 since device is not 3-wire
    # n is 0 since it is ignored to to W=0
    # T is 0 since the pi is little endian by default
    # R is 1 since the ADC is big endian
    # b is 0 since using main SPI

    # SPI setup options
    SPI_FLAGS   = 0x00008001
    SPI_BAUD    = 256000
    SPI_CHANNEL = 0  # CE is on pin 8

    SPI_CMD_DELAY = 500.0 / 100000.0

    # commands

    # write register 0 to set gain to 4, register 1 to enable continuous conversion
    # 0x41 sends WREG with register offset of 0 and to write 2 bytes from that point
    # the first byte in setup reg is the aforementioned WREG and the following bytes
    # are the values being written to the reigsters
    SETUP_REG     = bytearray([0x41, 0x0A, 0x04])
    # read all the registers for debugging
    READ_ALL_REG  = bytearray([0x23, 0x00, 0x00, 0x00, 0x00])
    RDATA         = bytearray([0x10, 0x00, 0x00])
    START         = bytearray([0x08]) # starts the continuous conversion
    RESET         = bytearray([0x06]) # resets the ADC

    def __init__(self):
        self.channel_open = False
        self.spi_handle = None
        self.pi = pigpio.pi()

    def open_channel(self):
        """Opens the connection to the ADC."""
        self.spi_handle = self.pi.spi_open(self.SPI_CHANNEL, self.SPI_BAUD, self.SPI_FLAGS)
        self.channel_open = True

    def power_on_setup(self):
        """Sends setup commands to the pH sensor ADC."""
        # open a SPI channel if not open
        if not self.channel_open:
            self.open_channel()

        #try:
        # set up the ADC for conversions
        self.pi.spi_write(self.spi_handle, self.RESET)
        time.sleep(self.SPI_CMD_DELAY)
        self.pi.spi_write(self.spi_handle, self.SETUP_REG)
        time.sleep(self.SPI_CMD_DELAY)
        self.pi.spi_write(self.spi_handle, self.START)
        time.sleep(self.SPI_CMD_DELAY)

        '''    print('Success')
        except:
            print('Failed to setup')
        finally:'''
        # cleanup
        self.close_channel()

    def _adc_conversion(self, reading):
        VREF = 2.048
        GAIN = 16

        # conversion factor from ADC datasheet equation 16
        factor = (2 * VREF / GAIN) / (2 ** 16)

        # convert the reading to an integer ignoring the first byte
        reading_to_int = struct.unpack('>H', reading[1:])[0]

        return factor * reading_to_int

    def pH_reading(self):
        """Sends the read command to the pH sensor ADC and returns the result

        :returns: a floating point number with the lastest pH sensor reading

        """
        # open a SPI channel if not open
        if not self.channel_open:
            self.open_channel()

        # read the ADC
        reading = None
        try:
            (count, reading) = self.pi.spi_xfer(self.spi_handle, self.RDATA)

            print('Count: {}, Reading: {}'.format(count, repr(reading)))
        except:
            print('Failed to read pH Sensor')
        finally:
            # cleanup
            self.close_channel()

            return self._adc_conversion(reading)

    def close_channel(self):
        """Closes the SPI channel to the ADC."""
        self.pi.spi_close(self.spi_handle)
        self.channel_open = False
        self.spi_handle = None

def parse_cmd_args():
    """Parses the command line args for setup and read options."""
    parser = argparse.ArgumentParser(description='Choose pH reading mode (Setup and/or Read)')

    parser.add_argument('--setup',
                        action='store_true',
                        help='Sets the pH sensor ADC to the proper read mode')
    parser.add_argument('--read',
                        action='store_true',
                        help='Reads the last value read by the pH sensor ADC')

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_cmd_args()

    sensor = PHSensor()

    if args.setup:
        # send setup commands
        sensor.power_on_setup()
    else:
        pass

    # still want to try and read if setup before read didn't happen
    if args.read:
        # read the latest value on the ADC (assumes setup already happened)
        print(sensor.pH_reading())
    else:
        pass
