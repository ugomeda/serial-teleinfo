class TeleinfoException(Exception):
    pass


class ParserException(TeleinfoException):
    pass


class InvalidChecksumException(ParserException):
    pass


class UnknownKeyException(ParserException):
    def __init__(self, key):
        self.key = key
        self.message = "The key {key} is not known"
