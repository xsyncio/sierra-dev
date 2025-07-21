import typing

_T = typing.TypeVar("_T")


class SierraOption(typing.Generic[_T]):
    """
    Wrapper for marking a function parameter as a Sierra option.

    Parameters
    ----------
    description : str, default ""
        A short description of the parameter.
    mandatory : typing.Literal["MANDATORY"] | None, default None
        Flags the parameter as mandatory.
    """

    def __init__(
        self,
        *,
        description: str = "",
        mandatory: typing.Literal["MANDATORY"] | None = None,
    ) -> None:
        self.description = description
        self.mandatory = mandatory


Param = typing.Annotated
