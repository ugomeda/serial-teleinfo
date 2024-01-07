import re
from typing import Tuple

from serial_teleinfo.exception import InvalidChecksumException, ParserException

SEPARATOR = b"\x20"
MATCHER = re.compile(b"^([^\x20\x09]+)([\x20\x09])(.+)([\x20\x09])([\x20-\x7e])$")


def parse_line(line: bytes) -> Tuple[str, str, bool]:
    """Parses a line and verifies the checksum according to the specification
    available at https://www.enedis.fr/sites/default/files/Enedis-NOI-CPT_02E.pdf.

    Returns:
        (str, str, bool): A tuple containing the key, its value and
            a boolean at True if this is the end of a frame

    Raises:
        InvalidChecksumException: If the checksum was not correct
        ParserException: If separators could not be matched
    """
    # Remove markers
    end_of_frame = line.endswith(b"\r\x03\x02\n")
    if end_of_frame:
        line = line[0:-4]
    elif line.endswith(b"\r\n"):
        line = line[0:-2]
    else:
        raise ParserException(f"Could not find markers in {line}")

    # Split the line into its parts
    match = MATCHER.match(line)
    if match is None:
        raise ParserException(f"Could not extract data from {line}")

    key = match.group(1)
    separator_1 = match.group(2)
    value = match.group(3)
    checksum = match.group(5)

    # Verify the checksum
    checksum_sum = sum(key) + sum(separator_1) + sum(value)
    checksum_value = (checksum_sum & 0x3F) + 0x20

    if ord(checksum) != checksum_value:
        raise InvalidChecksumException(
            f"Expected checksum of {checksum_value}, found {checksum}"
        )

    return key.decode("ASCII"), value.decode("ASCII"), end_of_frame
