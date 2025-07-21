import inspect
import typing

import httpx

import sierra.abc.sierra as sierra_abc_sierra
import sierra.internal.logger as sierra_internal_logger
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
        use_httpx_client: httpx.Client | None = None,
        logger: sierra_internal_logger.UniversalLogger | None = None,
    ) -> None:
        self.name = name
        self.description = description
        self.params: list[sierra_abc_sierra.SierraInvokerParam] = []
        self.http_client: httpx.Client | None = use_httpx_client
        self.logger: sierra_internal_logger.UniversalLogger = (
            logger
            if logger is not None
            else sierra_internal_logger.UniversalLogger(
                name=self.name,
                level=sierra_internal_logger.LogLevel.BASIC,
            )
        )
        self._entry_point: _TCallable
        self.deps: list[_TCallable] = []
        self.requirements: list[str] = []
        self.command: str = ""
        self.filename = ""

    @staticmethod
    def verify_signature(func: _TCallable) -> None:
        """
        Verifies that all parameters are properly typed with SierraOption metadata.
        Raises TypeError if any parameter lacks SierraOption typing.

        Parameters
        ----------
        func : _TCallable
            The function to verify.

        Raises
        ------
        TypeError
            If any parameter lacks proper SierraOption annotation.
        """
        sig = inspect.signature(func)
        for name, param in sig.parameters.items():
            annotation = param.annotation
            if typing.get_origin(annotation) is not typing.Annotated:
                raise TypeError(
                    f"Parameter '{name}' must use Annotated with SierraOption"
                )
            args = typing.get_args(annotation)
            if not any(
                isinstance(arg, sierra_options.SierraOption)
                for arg in args[1:]
            ):
                raise TypeError(
                    f"Parameter '{name}' is missing SierraOption metadata."
                )

    def entry_point(self, func: _TCallable) -> _TCallable:
        """
        Register a Python function as an invoker script.

        This extracts parameter metadata and prepares the function for code generation.

        Parameters
        ----------
        func : _TCallable
            The function to register.

        Returns
        -------
        _TCallable
            The original function (unchanged).
        """
        self.filename = inspect.getfile(func)
        self.verify_signature(func)
        self._entry_point = func
        # Extract parameter metadata
        sig = inspect.signature(func)
        for name, param in sig.parameters.items():
            annotation = param.annotation
            if typing.get_origin(annotation) is typing.Annotated:
                args = typing.get_args(annotation)
                param_type = args[0]

                for meta in args[1:]:
                    if isinstance(meta, sierra_options.SierraOption):
                        options: str | None = None
                        if meta.mandatory == "MANDATORY":
                            options = "MANDATORY"

                        generated_param = sierra_abc_sierra.SierraInvokerParam(
                            Name=name,
                            Type=param_type,
                            Description=meta.description,
                            Options=options,
                        )
                        self.params.append(generated_param)

        return func

    def dependancy(self, func: _TCallable) -> _TCallable:
        self.deps.append(func)
        return func

    def requirement(self, requirement: list[str]) -> None:
        self.requirements.extend(requirement)
