import typing

_T = typing.TypeVar("_T")


class SierraOption(typing.Generic[_T]):
    """Wrapper for marking a function parameter as a Sierra option."""

    def __init__(
        self,
        *,
        description: str = "",
        mandatory: typing.Literal["MANDATORY"] | None = None,
    ) -> None:
        self.description = description
        self.mandatory = mandatory


# alias to typing.Annotated
Param = typing.Annotated


"""Example
def example(name: Param[str, SierraOption(description="lingam")]):
    print("radnom lmao", name)
"""
