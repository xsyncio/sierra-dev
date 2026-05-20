"""
Sierra ABC Schema Models.
=========================

Typed dictionary models defining the structural contracts for invoker
scripts, parameters, and top-level configurations. These are used
throughout the compiler and builder pipelines.
"""

import typing

import sierra.abc.base as sierra_abc_base


class SierraInvokerParam(sierra_abc_base.SierraABC):
    """
    Represents a single parameter for an invoker script.

    Attributes
    ----------
    Name : str
        The parameter's name (must be a valid Python identifier).
    Description : str or None
        Human-readable description of the parameter.
    Type : Any
        The data type of the parameter (e.g., ``str``, ``int``, ``pathlib.Path``,
        ``Image``).
    Options : list[str] or None
        List of constraint flags. Supported values:
        - ``"MANDATORY"`` — execution is blocked if the value is empty.
        - ``"PRIMARY"`` — SIERRA auto-populates from the active node value.
    """

    Name: str
    Type: typing.Any
    Description: str | None
    Options: list[str] | None
    MinValue: int | float | None
    MaxValue: int | float | None
    Choices: list[typing.Any] | None
    Pattern: str | None


class SierraInvokerScript(sierra_abc_base.SierraABC):
    """
    Represents an invoker script definition.

    Attributes
    ----------
    Name : str
        Unique name of the script.
    Description : str or None
        Brief description of the script.
    Protocol : str or None
        The execution protocol (``"V1"`` for batch, ``"V2"`` for streaming).
    Params : list[SierraInvokerParam] or None
        List of parameters for the script.
    Command : str or None
        Shell or Python command template, with placeholders for parameters.
    """

    Name: str
    Description: str | None
    Protocol: typing.Literal["V1", "V2"] | None
    Params: list[SierraInvokerParam] | None
    Command: str | None


class SierraConfig(sierra_abc_base.SierraABC):
    """
    Top-level configuration for SIERRA invoker scripts.

    Attributes
    ----------
    PATHS : list[str] or None
        Optional list of directories to search for scripts.
    SCRIPTS : list[SierraInvokerScript]
        Definitions of all invoker scripts.
    """

    PATHS: list[str] | None
    SCRIPTS: list[SierraInvokerScript]
