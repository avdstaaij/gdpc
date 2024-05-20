"""Contains exceptions used by GDPC"""


class InterfaceError(RuntimeError):
    """An error occured when communicating with the GDMC HTTP interface"""


class InterfaceConnectionError(InterfaceError):
    """An error occured when trying to connect to the GDMC HTTP interface"""


class InterfaceInternalError(InterfaceError):
    """The GDMC HTTP interface reported an internal server error (500)"""


class BuildAreaNotSetError(InterfaceError):
    """Attempted to retrieve the build area while it was not set"""
