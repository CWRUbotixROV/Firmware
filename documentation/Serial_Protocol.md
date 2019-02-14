# Serial Protocol

# Raspberry Pi <-> Arduino

## Overall Message

||**Byte 1**|**Byte 2**|**Byte 3**|**Byte 4**|**...**|**Byte N + 4**|**Byte N + 5**|**Byte N + 6**|**Byte N + 7**|
|--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
|**Master** *(RPi)*|[OP Code](#op-codes)|[CRC](#crc)|NOP|[Data Packet](#data-packet) Byte 1|...|[Data Packet](#data-packet) Byte N|[CRC](#crc)|NOP|NOP| 
|**Slave** *(Arduino)*|NOP|NOP|[ACK/ERR](#ack-err)|NOP|...|NOP|NOP|[ACK/ERR](#ack-err)|[DONE/ERR](#done-err)|

To further explain what would happen for a serial transmission, suppose the master sent some [OP Code](#op-codes) (byte 1) along with a [CRC](#crc) (byte 2) calculated over the OP Code byte.

The slave would then send back an acknowlegement ([ACK/ERR](#ack-err) in byte 3) that it received the command if the [OP Code](#op-codes) is valid and the [CRC](#crc) matches (`0xFF` on success, `0x00` on failure).  If the [OP Code](#op-codes) does not have a [data packet](#data-packet) associated with it, the [data packet](#data-packet) part of the transmission is skipped and the master waits for the slave to respond with [DONE/ERR](#done-err) (bytes 4 through N + 6 are skipped and byte 4 becomes the DONE/ERR in byte N + 7)

Once the slave acknowledges that it is ready to receive the [data packet](#data-packet) (bytes 4 through N + 4) from the master, the master will begin transmitting the bytes in the [data packet](#data-packet) (assumign there is one).  Once the master finishes sending the [data packet](#data-packet), it will send a [CRC](#crc) (byte N + 5) that it calculated over the data.

The slave will then respond to the master with acknowledgement ([ACK/ERR](#ack-err) in byte N + 6) that it received the [data packet](#data-packet) and a matching [CRC](#crc) with `0xFF`.  If there are errors, it will instead send back `0x00`.  

The slave will then perform the command requested by the master.  Once it finishes performing the command, it will send back a (`0xFF`) (([DONE/ERR](#done-err) value in byte N + 7) unless it failed due to some error, in which case it will send `0x00` instead.

### OP Codes

|Command|OP Code|
|:--|:--:|
|[Write Servo](#write-servo)|`0x01`|

### ACK ERR

ACK/ERR is the response from the slave that it is finished receiving data from the master.  If it received a valid [OP Code](#op-codes) or [Data Packet](#data-packet) and a valid corresponding [CRC](#crc), the slave will send back `0xFF`.  Otherwise, there was an error and the slave will send back something that is not `0xFF` (specifically, it will send `0x00`).

### DONE ERR

DONE/ERR is the response from the slave that it finished performing the command requested by the master.  If the command was successful the slave will send back `0xFF`.  Otherwise, there was an error and the slave will send back something that is not `0xFF` (specifically, it will send `0x00`).

### Data Packet

The data packet contains the information that is necessary to perform the command. Some commands may not send any data along with the OP Code.  For these commands, the 

The following commands are defined:

- [Write Servo](#write-servo)

### CRC

The CRC is calculated over the preceding byte(s) using the following polynomial

`x^8 + x^2 + x + 1`

## Data Packet Formats for Commands

### Write Servo

|**Byte 0**|
|:--:|
|Value between 0-180 that specified the angle to set the servo to|