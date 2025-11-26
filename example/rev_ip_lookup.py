import requests

import sierra

invoker = sierra.InvokerScript(
    name="reverse_ip",
    description="Perform reverse IP lookup using HackerTarget API",
)

invoker.requirement(["requests"])


@invoker.dependancy
def get_reverse_ip(ip: str) -> list[str]:
    """
    Query reverse IP records using HackerTarget API.

    Parameters
    ----------
    ip : str
        IP address to lookup.

    Returns
    -------
    list of str
        List of domains hosted on the given IP.
    """
    res = requests.get(f"https://api.hackertarget.com/reverseiplookup/?q={ip}")
    if "error" in res.text.lower():
        return []
    return list(set(res.text.splitlines()))


@invoker.entry_point
def run(
    ip: sierra.Param[
        str | None,
        sierra.SierraOption(
            description="IP address to reverse resolve.",
            mandatory="MANDATORY",
        ),
    ],
) -> None:
    """Entry point for reverse IP lookup."""
    if ip is None:
        result = sierra.create_error_result("Missing IP address")
    else:
        domains = get_reverse_ip(ip)
        # Fix the type issue by creating the correct structure
        tree_data: list[str | dict[str, list[str]]] = []
        for domain in domains:
            tree_data.append({"🌐 Domain": [domain]})
        result = sierra.create_tree_result(tree_data)
    sierra.respond(result)


def load(client: sierra.SierraDevelopmentClient) -> None:
    client.load_invoker(invoker)
