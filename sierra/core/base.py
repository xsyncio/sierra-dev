import typing

if typing.TYPE_CHECKING:
    import sierra.client as sierra_client


class SierraCoreObject:
    def __init__(
        self, client: "sierra_client.SierraDevelopmentClient"
    ) -> None:
        self.client = client
