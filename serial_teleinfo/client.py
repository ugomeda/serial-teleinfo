import serial

from serial_teleinfo.parser import parse_line
from serial_teleinfo.types import type_parsers, Value
from serial_teleinfo.exception import (
    ParserException,
    UnknownKeyException,
)


class Client:
    def __init__(self, port: str = "/dev/ttyUSB0"):
        self._port = port
        self._serial = None

    def __enter__(self) -> "Client":
        """ Opens the connections to the serial port.

        Raises:
            serial.SerialException: If an error occured while establishing the connection
        """
        self._serial = serial.Serial(
            self._port,
            baudrate=1200,
            bytesize=serial.SEVENBITS,
            parity=serial.PARITY_EVEN,
            stopbits=serial.STOPBITS_ONE,
            xonxoff=False,
            timeout=1,
        )

        # Read first line as it will not be complete
        try:
            self._serial.readline()
        except:
            self._serial.close()

            raise

        return self

    def __exit__(self, type, value, traceback):
        if self._serial is not None:
            self._serial.close()

    def _raw_line(self) -> bytes:
        """ Returns next line read on the serial port
        """
        return self._serial.readline()

    def read_line(self) -> (str, str):
        """ Parses the next line and returns it as a key, value pair

        Raises:
            ParserException: If the line could not be decoded
        """
        return parse_line(self._raw_line())

    def read_value(self) -> Value:
        """ Parses the next line and returns it as a Value object
        """
        key, value, end_of_frame = self.read_line()

        # Parse the data
        parser = type_parsers.get(key)
        if parser is None:
            raise UnknownKeyException(key=key)

        return parser(key, value, end_of_frame)
