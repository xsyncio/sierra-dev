import typing

if typing.TYPE_CHECKING:
    import sierra.client as sierra_client

"""
Module providing the SierraCoreObject base class.

This module defines the SierraCoreObject, which serves as the foundational class
for all Sierra components, ensuring each component has access to a common
SierraDevelopmentClient for logging and API interactions.
"""


class SierraCoreObject:
    """
    Base class for Sierra core objects.

    Parameters
    ----------
    client : SierraDevelopmentClient
        Client instance used for operations, providing logger and HTTP access.
    """

    def __init__(
        self, client: "sierra_client.SierraDevelopmentClient"
    ) -> None:
        """
        Initialize a SierraCoreObject.

        Parameters
        ----------
        client : SierraDevelopmentClient
            The Sierra development client.

        Notes
        -----
        Logs each initialization step via the client's logger.
        """
        # Assign client instance
        self.client = client  # type: ignore[name-defined]
        # Log the start of initialization
        self.client.logger.log(
            message=f"Initializing SierraCoreObject with client: {client}",
            log_type="debug",
        )
        # Confirm assignment of client
        self.client.logger.log(
            message="SierraCoreObject.client set successfully",
            log_type="debug",
        )
