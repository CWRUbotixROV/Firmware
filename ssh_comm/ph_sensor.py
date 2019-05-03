import pigpio as pi  # this might be the wrong import
import argparse

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

    # commands
    RDATA         = 0x10
    CONTINUOUS_CM = 0x0 # continuous conversion mode
    DRDYM         = [0x00, 0x00]

    def __init__():
        self.channel_open = False
        self.spi_handle = None

    def open_channel(self):
        """Opens the connection to the ADC."""
        self.spi_handle = pi.spi_open(self.SPI_CHANNEL, self.SPI_BAUD, self.SPI_CHANNEL)
        self.channel_open = True

    def power_on_setup(self):
        """Sends setup commands to the pH sensor ADC."""
        # open a SPI channel if not open
        if not self.channel_open:
            self.open_channel()

        try:
            # set up the ADC for conversions
            pi.spi_xfer(spi_handle, CONTINUOUS_CM)
            pi.spi_xfer(spi_handle, DRDYM)

            print('Success')
        except:
            print('Failed to setup')
        finally:
            # cleanup
            self.close_channel()

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
            (count, reading) = pi.spi_xfer(spi_handle, RDATA)
        except:
            print('Failed to read pH Sensor')
        finally:
            # cleanup
            self.close_channel()

            return reading

    def close_channel(self):
        """Closes the SPI channel to the ADC."""
        pi.spi_close(self.spi_handle)
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
