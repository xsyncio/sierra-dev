import pathlib

import sierra.abc.base as sierra_abc_base


class Environment(sierra_abc_base.SierraABC):
    name: str
    path: pathlib.Path


class SideLoader(sierra_abc_base.SierraABC):
    """
    Base class for side loaders.

    Attributes
    ----------
    name : str
        Name of the side loader.
    path : pathlib.Path
        Path to the side loader directory.
    """

    path: pathlib.Path
