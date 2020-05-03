import serial
from serial_teleinfo import Client, TeleinfoException

try:
    with Client("/dev/ttyUSB0") as client:
        while True:
            print(client.read_value())
except TeleinfoException as e:
    print(e)
except serial.SerialException as e:
    print(e)
