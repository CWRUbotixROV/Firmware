import os
import glob
import time

'''
Setup info:

Red connects to 3.3V, Blue connects to ground and Yellow is data (pin 7 which is GPIO04)
4.7 kOhm resistor between data and VCC

'''
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

bad_crc = True

while bad_crc:
    with open(device_file, 'r') as f:

        lines = f.readlines()

        # check the CRC
        crc_line = lines[0]
        crc = crc_line.split(' ')[-1]

        # make sure the CRC is correct
        if crc == 'YES\n':
            # read the temperature
            temp_line = lines[-1]  # 0x 0x 0x ... t=#####
            temp_str = temp_line.split(' ')[-1]  # t=#####

            temp = float(temp_str.split('t=')[-1]) / 1000  # ##.###

            # output the result
            print(temp)

            bad_crc = False
