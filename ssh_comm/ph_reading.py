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

spi_flags = 0x00008001
spi_baud = 256000
spi_channel = 0  # CE is on pin 8

RDATA = 0x10
CONTINUOUS_CM = 0x0
DRDYM = [0x00, 0x00]
