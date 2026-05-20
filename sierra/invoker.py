"""
Sierra Invoker Script.
======================

The core ``InvokerScript`` class that developers use to define, annotate,
and register SIERRA invoker scripts. Supports V1 (batch) and V2 (streaming)
protocols, ``STRING``, ``FILE``, and ``IMAGE`` parameter types, and
``PRIMARY`` + ``MANDATORY`` option flags.

Usage
-----
    import sierra

    invoker = sierra.InvokerScript(
        name="subdomain_finder",
        description="Discover subdomains for a target domain",
        protocol="V2",
    )

    @invoker.entry_point
    def run(domain: str, timeout: int = 30) -> None:
        '''
        Subdomain discovery tool.

        Parameters
        ----------
        domain : str
            Target domain to enumerate.
        timeout : int
            Request timeout in seconds.
        '''
        ...
"""

import inspect
import pathlib
import re
import typing

import sierra.abc.sierra as sierra_abc_sierra
import sierra.options as sierra_options

__all__ = ["InvokerScript"]

_TCallable = typing.Callable[..., typing.Any]


class InvokerScript:
    """
    Typed invoker script wrapper for building SIERRA canvas integrations.

    Generates ``config.yaml`` entries and standalone argparse-compatible
    Python scripts from annotated function signatures.

    Parameters
    ----------
    name : str
        Unique identifier for the invoker. Must be a valid Python identifier
        (lowercase + underscores recommended).
    description : str or None
        Brief description shown in the SIERRA canvas context menu.
    protocol : Literal["V1", "V2"]
        Execution protocol:
        - ``"V1"`` (default): Batch mode — script runs to completion, outputs
          a single JSON block.
        - ``"V2"``: Streaming mode — script emits incremental JSON events
          line-by-line to stdout in real-time.

    Attributes
    ----------
    name : str
        The unique name of the script.
    description : str or None
        A short description of the script.
    protocol : Literal["V1", "V2"]
        The execution protocol version.
    params : list[SierraInvokerParam]
        List of extracted parameter metadata.
    deps : list[Callable]
        List of registered dependency functions.
    requirements : list[str]
        List of pip package requirements.
    command : str or None
        The generated CLI command template.
    filename : pathlib.Path
        Path to the source file containing the entry point.
    """

    def __init__(
        self,
        name: str,
        description: str | None = None,
        protocol: typing.Literal["V1", "V2"] = "V1",
    ) -> None:
        # Validate name at construction time
        if not name or not name.strip():
            raise ValueError("InvokerScript name must not be empty.")

        self.name: str = name
        self.description: str | None = description
        self.protocol: typing.Literal["V1", "V2"] = protocol
        self.params: list[sierra_abc_sierra.SierraInvokerParam] = []
        self._entry_point: _TCallable
        self.deps: list[_TCallable] = []
        self.requirements: list[str] = []
        self.command: str | None = None
        self.filename: pathlib.Path

    # ------------------------------------------------------------------
    # Signature verification
    # ------------------------------------------------------------------

    @staticmethod
    def verify_signature(func: _TCallable) -> None:
        """
        Verify that function parameters are valid for invoker generation.

        Rejects ``*args`` and ``**kwargs`` — all parameters must be named.

        Parameters
        ----------
        func : Callable
            The function to verify.

        Raises
        ------
        TypeError
            If variadic parameters are found.
        """
        sig = inspect.signature(func)
        for name, param in sig.parameters.items():
            if name == "self":
                continue
            if param.kind in (
                inspect.Parameter.VAR_POSITIONAL,
                inspect.Parameter.VAR_KEYWORD,
            ):
                raise TypeError(f"Variadic parameter '{name}' is not supported")

    # ------------------------------------------------------------------
    # Docstring parsing
    # ------------------------------------------------------------------

    def _extract_param_descriptions(self, docstring: str | None) -> dict[str, str]:
        """
        Extract parameter descriptions from docstring.

        Supports Google-style, Sphinx-style, and NumPy-style docstrings.

        Parameters
        ----------
        docstring : str or None
            The function's docstring.

        Returns
        -------
        dict[str, str]
            Mapping of parameter names to their descriptions.
        """
        if not docstring:
            return {}

        descriptions: dict[str, str] = {}
        lines = inspect.cleandoc(docstring).split("\n")

        param_pattern = re.compile(r"^\s*(\w+)(?:\s*\(.*\))?\s*:\s*(.*)$")

        in_params = False
        current_param: str | None = None

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            # Check for section headers
            if stripped.lower() in (
                "parameters",
                "parameters:",
                "args",
                "args:",
                "arguments",
                "arguments:",
            ):
                in_params = True
                continue

            if stripped.startswith("---") or stripped.startswith("==="):
                continue

            if in_params:
                # Check if we exited params section
                if (
                    stripped.endswith(":")
                    and " " not in stripped
                    and not param_pattern.match(stripped)
                ):
                    break

                match = param_pattern.match(stripped)
                if match:
                    current_param = match.group(1)
                    descriptions[current_param] = match.group(2)
                elif current_param is not None and (
                    line.startswith("    ") or line.startswith("\t")
                ):
                    descriptions[current_param] += " " + stripped
                elif " : " in stripped:
                    parts = stripped.split(" : ", 1)
                    current_param = parts[0].strip()

        return descriptions

    # ------------------------------------------------------------------
    # Type resolution helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _is_image_type(type_obj: typing.Any) -> bool:
        """Check if a type annotation represents the Image parameter type."""
        if isinstance(type_obj, type):
            if type_obj.__name__ == "Image":
                return True
            # Check MRO for Image ancestry
            for cls in getattr(type_obj, "__mro__", ()):
                if cls.__name__ == "Image":
                    return True
        return str(type_obj) == "Image" or "Image" in str(type_obj)

    @staticmethod
    def _is_path_type(type_obj: typing.Any) -> bool:
        """Check if a type annotation represents a file path."""
        if isinstance(type_obj, type):
            if type_obj.__name__ == "Path" or type_obj.__module__ == "pathlib":
                return True
            for cls in getattr(type_obj, "__mro__", ()):
                if cls.__name__ in ("Path", "PurePath"):
                    return True
        return str(type_obj) == "Path" or "pathlib.Path" in str(type_obj)

    # ------------------------------------------------------------------
    # Entry point registration
    # ------------------------------------------------------------------

    def entry_point(self, func: _TCallable) -> _TCallable:
        """
        Register a Python function as the invoker's entry point.

        Extracts parameter metadata from the function signature and
        docstring. Supports both ``Annotated[T, SierraOption]`` and
        plain type annotations.

        Parameters
        ----------
        func : Callable
            The function to register.

        Returns
        -------
        Callable
            The original function (unmodified).

        Raises
        ------
        ValueError
            If the function has no parameters.
        TypeError
            If variadic parameters are found.
        """
        self.filename = pathlib.Path(inspect.getfile(func))
        self.verify_signature(func)
        self._entry_point = func

        # Extract parameter descriptions from docstring
        doc_descriptions = self._extract_param_descriptions(func.__doc__)

        sig = inspect.signature(func)
        for name, param in sig.parameters.items():
            annotation = param.annotation

            # Defaults
            is_mandatory = param.default is inspect.Parameter.empty
            default_desc = doc_descriptions.get(name, "")
            param_type = annotation
            options: list[str] = []
            is_primary = False
            min_val = None
            max_val = None
            choices_val = None
            pattern_val = None

            if is_mandatory:
                options.append("MANDATORY")

            # Check for Annotated[T, SierraOption(...)]
            if typing.get_origin(annotation) is typing.Annotated:
                args = typing.get_args(annotation)
                param_type = args[0]

                for meta in args[1:]:
                    if isinstance(meta, sierra_options.SierraOption):
                        if meta.description:
                            default_desc = meta.description
                        if meta.mandatory == "MANDATORY":
                            if "MANDATORY" not in options:
                                options.append("MANDATORY")
                        elif meta.mandatory is None and not is_mandatory:
                            # Explicitly optional
                            options = [o for o in options if o != "MANDATORY"]
                        if meta.primary:
                            is_primary = True
                        if meta.min_value is not None:
                            min_val = meta.min_value
                        if meta.max_value is not None:
                            max_val = meta.max_value
                        if meta.choices is not None:
                            choices_val = meta.choices
                        if meta.pattern is not None:
                            pattern_val = meta.pattern

            if is_primary and "PRIMARY" not in options:
                options.append("PRIMARY")

            # Handle Optional[T] / Union[T, None]
            if typing.get_origin(param_type) in (typing.Union,):
                args = typing.get_args(param_type)
                non_none = [a for a in args if a is not type(None)]
                if len(non_none) == 1:
                    param_type = non_none[0]

            generated_param = sierra_abc_sierra.SierraInvokerParam(
                Name=name,
                Type=param_type,
                Description=default_desc,
                Options=options if options else None,
            )
            if min_val is not None:
                generated_param["MinValue"] = min_val
            if max_val is not None:
                generated_param["MaxValue"] = max_val
            if choices_val is not None:
                generated_param["Choices"] = choices_val
            if pattern_val is not None:
                generated_param["Pattern"] = pattern_val

            self.params.append(generated_param)

        if not self.params:
            raise ValueError(f"Invoker '{self.name}' must have at least one parameter.")

        return func

    # ------------------------------------------------------------------
    # Dependency management
    # ------------------------------------------------------------------

    def dependancy(self, func: _TCallable) -> _TCallable:
        """
        Register a dependency function that will be inlined into the
        compiled standalone script.

        Parameters
        ----------
        func : Callable
            The dependency function.

        Returns
        -------
        Callable
            The original function (unmodified).
        """
        self.deps.append(func)
        return func

    def requirement(self, requirement: list[str]) -> None:
        """
        Add pip package requirements for this invoker.

        Parameters
        ----------
        requirement : list[str]
            List of pip package specifiers (e.g. ``["requests", "dnspython>=2.0"]``).
        """
        self.requirements.extend(requirement)

    def set_command(self, command: str) -> None:
        """
        Set the generated CLI command template.

        Parameters
        ----------
        command : str
            The command string with parameter placeholders.
        """
        self.command = command
