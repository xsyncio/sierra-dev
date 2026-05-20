"""
Sierra Options.
===============

Type-safe option descriptors for annotating invoker script parameters.

Usage
-----
    import sierra

    @invoker.entry_point
    def run(
        domain: sierra.Param[
            str,
            sierra.SierraOption(
                description="Target domain to scan",
                mandatory="MANDATORY",
                primary=True,
            )
        ],
    ) -> None:
        ...
"""

import typing

__all__ = ["SierraOption", "Param"]

_T = typing.TypeVar("_T")


class SierraOption[T]:
    """
    Typed descriptor for marking a function parameter as a SIERRA option.

    Provides metadata that controls how the parameter appears in the
    generated ``config.yaml`` and how SIERRA presents it to the user.

    Parameters
    ----------
    description : str
        Human-readable description of the parameter. Shown as a tooltip
        in the SIERRA canvas input dialog.
    mandatory : Literal["MANDATORY"] or None
        Set to ``"MANDATORY"`` to block execution when the value is empty.
        Defaults to ``None`` (optional parameter).
    primary : bool
        If ``True``, this parameter is flagged as ``PRIMARY`` in the YAML
        output, meaning SIERRA auto-populates it from the active node's
        value. Only one parameter per script should be primary.

    Examples
    --------
    >>> from sierra import SierraOption, Param
    >>> def scan(
    ...     target: Param[str, SierraOption(description="IP address", mandatory="MANDATORY", primary=True)],
    ...     timeout: Param[int, SierraOption(description="Request timeout in seconds")] = 30,
    ... ) -> None:
    ...     ...
    """

    __slots__ = (
        "description",
        "mandatory",
        "primary",
        "min_value",
        "max_value",
        "choices",
        "pattern",
    )

    def __init__(
        self,
        *,
        description: str = "",
        mandatory: typing.Literal["MANDATORY"] | None = None,
        primary: bool = False,
        min_value: int | float | None = None,
        max_value: int | float | None = None,
        choices: list[typing.Any] | None = None,
        pattern: str | None = None,
    ) -> None:
        self.description: str = description
        self.mandatory: typing.Literal["MANDATORY"] | None = mandatory
        self.primary: bool = primary
        self.min_value: int | float | None = min_value
        self.max_value: int | float | None = max_value
        self.choices: list[typing.Any] | None = choices
        self.pattern: str | None = pattern

    def __repr__(self) -> str:
        parts: list[str] = []
        if self.description:
            parts.append(f"description={self.description!r}")
        if self.mandatory:
            parts.append(f"mandatory={self.mandatory!r}")
        if self.primary:
            parts.append("primary=True")
        if self.min_value is not None:
            parts.append(f"min_value={self.min_value}")
        if self.max_value is not None:
            parts.append(f"max_value={self.max_value}")
        if self.choices is not None:
            parts.append(f"choices={self.choices!r}")
        if self.pattern is not None:
            parts.append(f"pattern={self.pattern!r}")
        return f"SierraOption({', '.join(parts)})"


#: Convenience alias for ``typing.Annotated`` — used to annotate invoker
#: parameters with ``SierraOption`` metadata.
Param = typing.Annotated
