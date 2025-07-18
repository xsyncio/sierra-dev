import typing

import msgspec


class SierraABC(typing.TypedDict, total=False):
    """
    Base class for all Sierra ABCs.
    This class is used to define the structure of Sierra ABCs.
    """

    ...


class SierraDataStruct(msgspec.Struct):
    """
    Base class for all Sierra data structures.
    This class is used to define the structure of Sierra data structures.
    """

    ...
