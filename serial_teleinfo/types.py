from typing import Callable, List

from serial_teleinfo.exception import ParserException


class Value:
    def __init__(
        self, key: str, value: any, unit: str = None, end_of_frame: bool = False
    ):
        self.key = key
        self.value = value
        self.unit = unit
        self.end_of_frame = end_of_frame

    def __str__(self):
        end_of_frame = " (END OF FRAME)" if self.end_of_frame else ""
        if self.unit is None:
            return f'<{self.key}="{self.value}"{end_of_frame}>'
        else:
            return f"<{self.key}={self.value} {self.unit}{end_of_frame}>"


def value_converter(
    lengths: List[int], parser: Callable[[str], any] = None, unit: str = None
) -> Callable[[str, str], Value]:
    if unit is not None:
        if parser is not None:
            raise ValueError("Cannot provide an unit and a parser")

        parser = int

    if parser is None:
        parser = str

    def _value_converter(key: str, value: str, end_of_frame: bool = False) -> Value:
        value_length = len(value)
        if value_length not in lengths:
            raise ParserException(
                f"Expected value length in {lengths}, got {value_length}"
            )

        return Value(key, parser(value), unit, end_of_frame)

    return _value_converter


def parse_str_remove_ellipsis(value: str) -> str:
    return value.rstrip(".")


# Extracted from the official documentation
# https://www.enedis.fr/sites/default/files/Enedis-NOI-CPT_02E.pdf
#
# dict containing (possible lengths, parser, unit) of each key
#
# Does not support :
# - "Compteur Jaune electronique (CJE)"
# - "Interface Clientele Emeraude a deux quadrants (ICE-2Q)"
# - "Interface Clientele Emeraude a quatre quadrants (ICE-4Q)"
# - "Compteur PME-PMI"
# - "Compteur SAPHIR"
type_parsers = {
    # Page 23
    "ADCO": value_converter([12]),
    "OPTARIF": value_converter([4], parse_str_remove_ellipsis),
    "BASE": value_converter([8, 9], unit="Wh"),
    "HCHC": value_converter([8, 9], unit="Wh"),
    "HCHP": value_converter([8, 9], unit="Wh"),
    "EJPHN": value_converter([8, 9], unit="Wh"),
    "EJPHPM": value_converter([8, 9], unit="Wh"),
    "GAZ": value_converter([7], unit="dal"),
    "AUTRE": value_converter([7], unit="dal"),
    "PTEC": value_converter([4], parse_str_remove_ellipsis),
    "MOTDETAT": value_converter([6]),
    # Page 26
    "ISOUSC": value_converter([2], unit="A"),
    "BBRHCJB": value_converter([9], unit="Wh"),
    "BBRHPJB": value_converter([9], unit="Wh"),
    "BBRHCJW": value_converter([9], unit="Wh"),
    "BBRHPJW": value_converter([9], unit="Wh"),
    "BBRHCJR": value_converter([9], unit="Wh"),
    "BBRHPJR": value_converter([9], unit="Wh"),
    "PEJP": value_converter([2], unit="min"),
    "DEMAIN": value_converter([4], parse_str_remove_ellipsis),
    "IINST": value_converter([3], unit="A"),
    "ADPS": value_converter([3], unit="A"),
    "IMAX": value_converter([3], unit="A"),
    "HHPHC": value_converter([1]),
    # page 30
    "PAPP": value_converter([5], unit="VA"),
    # page 32
    "IINST1": value_converter([3], unit="A"),
    "IINST2": value_converter([3], unit="A"),
    "IINST3": value_converter([3], unit="A"),
    "IMAX1": value_converter([3], unit="A"),
    "IMAX2": value_converter([3], unit="A"),
    "IMAX3": value_converter([3], unit="A"),
    "PMAX": value_converter([5], unit="W"),
    "PPOT": value_converter([2]),
}
