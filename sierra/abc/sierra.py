import typing

import sierra.abc.base as sierra_abc_base


class SierraInvokerParam(sierra_abc_base.SierraABC):
    """
    Represents a single parameter for an invoker script.

    Attributes
    ----------
    Name : str
        The parameter's name.
    Description : str | None
        Human-readable description of the parameter.
    Type : str
        The data type of the parameter (e.g., 'STRING', 'FILE').
    Options : list[str] | None
        List of flags, such as 'PRIMARY' or 'MANDATORY'.
    """

    Name: str
    Type: str
    Description: str | None
    Options: typing.Literal["MANDATORY"] | None


class SierraInvokerScript(sierra_abc_base.SierraABC):
    """
    Represents an invoker script definition.

    Attributes
    ----------
    Name : str
        Unique name of the script.
    Description : str | None
        Brief description of the script.
    Params : list[SierraInvokerParam]
        List of parameters for the script.
    Command : str
        Shell or Python command template, with placeholders for parameters.
    """

    Name: str
    Description: str | None
    Params: list[SierraInvokerParam] | None
    Command: str | None


class SierraConfig(sierra_abc_base.SierraABC):
    """
    Top-level configuration for SIERRA invoker scripts.

    Attributes
    ----------
    PATHS : list[str] | None
        Optional list of directories to search for scripts.
    SCRIPTS : list[SierraInvokerScript]
        Definitions of all invoker scripts.
    """

    PATHS: list[str] | None
    SCRIPTS: list[SierraInvokerScript]
