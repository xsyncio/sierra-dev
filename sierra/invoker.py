import inspect
import pathlib
import typing

import sierra.abc.sierra as sierra_abc_sierra
import sierra.options as sierra_options

_TCallable = typing.Callable[..., typing.Any]


class InvokerScript:
    """
    A wrapper for creating Sierra invoker scripts that generates config.yaml and argparse-compatible scripts.

    This class is used to define a script with its parameters, then generate:
    1. A standalone Python script with argparse handling
    2. A YAML configuration for Sierra
    3. Proper JSON output formatting

    Attributes
    ----------
    name : str
        The unique name of the script.
    description : str | None
        A short description of the script.
    params : list[SierraInvokerParam]
        List of parameter metadata.
    http_client : httpx.Client | None
        Optional HTTP client used for external requests.
    logger : UniversalLogger
        Logger instance for capturing script activity.
    _entry_point : _TCallable | None
        The registered Python function.
    _output_dir : Path | None
        Directory to output generated files.
    """

    def __init__(
        self,
        name: str,
        description: str | None = None,
    ) -> None:
        self.name = name
        self.description = description
        self.params: list[sierra_abc_sierra.SierraInvokerParam] = []
        self._entry_point: _TCallable
        self.deps: list[_TCallable] = []
        self.requirements: list[str] = []
        self.command: str | None = None
        self.filename: pathlib.Path

    @staticmethod
    def verify_signature(func: _TCallable) -> None:
        """
        Verifies that parameters are valid.
        Now supports standard types, so this is less strict.
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

    def _extract_param_descriptions(self, docstring: str | None) -> dict[str, str]:
        """
        Extract parameter descriptions from docstring.
        Supports Google and NumPy styles (basic parsing).
        """
        if not docstring:
            return {}

        descriptions = {}
        lines = inspect.cleandoc(docstring).split("\n")
        
        import re
        
        # Regex for Google/Sphinx style: "param_name (type): description" or "param_name: description"
        param_pattern = re.compile(r"^\s*(\w+)(?:\s*\(.*\))?\s*:\s*(.*)$")
        
        # Find parameters section
        in_params = False
        current_param = None
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
                
            # Check for section headers
            if stripped.lower() in ("parameters", "parameters:", "args", "args:", "arguments", "arguments:"):
                in_params = True
                continue
            
            if stripped.startswith("---") or stripped.startswith("==="):
                continue
                
            if in_params:
                # Check if we exited params section (heuristic: new section header)
                if stripped.endswith(":") and " " not in stripped and not param_pattern.match(stripped):
                    break
                
                match = param_pattern.match(stripped)
                if match:
                    current_param = match.group(1)
                    descriptions[current_param] = match.group(2)
                elif current_param and (line.startswith("    ") or line.startswith("\t")):
                    # Continuation
                    descriptions[current_param] += " " + stripped
                elif " : " in stripped: # NumPy style "name : type"
                    parts = stripped.split(" : ", 1)
                    current_param = parts[0].strip()
                    # Description is usually on next lines, but we'll ignore complex NumPy parsing for now
                    # unless it's inline
        
        return descriptions

    def entry_point(self, func: _TCallable) -> _TCallable:
        """
        Register a Python function as an invoker script.
        Supports both Annotated[T, SierraOption] and standard types with docstrings.
        """
        self.filename = pathlib.Path(inspect.getfile(func))
        self.verify_signature(func)
        self._entry_point = func
        
        # Extract parameter descriptions from docstring
        doc_descriptions = self._extract_param_descriptions(func.__doc__)
        
        sig = inspect.signature(func)
        for name, param in sig.parameters.items():
            annotation = param.annotation
            
            # Default values
            is_mandatory = param.default == inspect.Parameter.empty
            default_desc = doc_descriptions.get(name, "")
            param_type = annotation
            options = "MANDATORY" if is_mandatory else None
            
            # Check for Annotated (Legacy/Advanced)
            if typing.get_origin(annotation) is typing.Annotated:
                args = typing.get_args(annotation)
                param_type = args[0]
                
                for meta in args[1:]:
                    if isinstance(meta, sierra_options.SierraOption):
                        if meta.description:
                            default_desc = meta.description
                        if meta.mandatory == "MANDATORY":
                            options = "MANDATORY"
                        elif meta.mandatory is None and not is_mandatory:
                             options = None
            
            # Handle Optional[T]
            if typing.get_origin(param_type) in (typing.Union, typing.Optional):
                args = typing.get_args(param_type)
                # Filter out NoneType
                non_none = [a for a in args if a is not type(None)]
                if len(non_none) == 1:
                    param_type = non_none[0]
            
            generated_param = sierra_abc_sierra.SierraInvokerParam(
                Name=name,
                Type=param_type,
                Description=default_desc,
                Options=options,
            )
            self.params.append(generated_param)

        if not self.params:
            raise ValueError(f"Invoker '{self.name}' must have at least one parameter.")

        return func

    def dependancy(self, func: _TCallable) -> _TCallable:
        self.deps.append(func)
        return func

    def requirement(self, requirement: list[str]) -> None:
        self.requirements.extend(requirement)

    def set_command(self, command: str) -> None:
        self.command = command
