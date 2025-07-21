class BaseSierraError(Exception):
    """Base class for all Sierra errors."""

    pass


class SierraPathError(BaseSierraError):
    """Raised when there is a problem with a filesystem path."""

    pass


class SierraPathNotFoundError(SierraPathError):
    """Raised when a required filesystem path does not exist."""

    pass


class SierraClientPathError(SierraPathError):
    """
    Raised when the SierraDevelopmentClient cannot load invokers
    because its `environment.script_path` (or a given file)
    is not found or is not a valid `.py` file.
    """

    pass


class SierraExecutionError(BaseSierraError):
    """Raised when an execution error occurs in Sierra."""

    pass


class SierraClientLoadError(BaseSierraError):
    """
    Raised when a dynamically-imported module
    contains no valid InvokerScript subclasses.
    """

    pass


class SierraHTTPError(BaseSierraError):
    """Raised when an HTTP request via Sierra's http client fails."""

    pass


class SierraCacheError(BaseSierraError):
    """Raised when a cache-related error occurs in Sierra."""

    pass
