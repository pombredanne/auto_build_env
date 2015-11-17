__author__ = 'sean-abbott'

class AbeError(Exception):
    """ Base Abe Exception """
    pass

class AbeConfigError(AbeError):
    """ Exception raised for errors raised when reading configuration

    Attributes:
        msg  -- explanation of the error
    """
    def __init__(self, msg):
        self.msg = msg

