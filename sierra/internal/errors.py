class BaseSierraError(Exception):
    """Base class for all Sierra errors."""

    pass


class SierraPathError(BaseSierraError): ...


class SierraPathNotFoundError(SierraPathError): ...


class SierraExecutionError(BaseSierraError):
    """Raised when an execution error occurs in Sierra."""

    pass


class SierraHTTPError(BaseSierraError): ...


class SierraCacheError(BaseSierraError):
    """Raised when a cache-related error occurs in Sierra."""

    pass
