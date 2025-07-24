import re

import requests

import sierra

invoker = sierra.InvokerScript(
    name="whois-email-extractor",
    description="Extract emails from WHOIS records",
)

invoker.requirement(["requests"])


@invoker.dependancy
def fetch_whois_emails(domain: str) -> list[str]:
    """
    Extract email addresses from WHOIS raw data.

    Parameters
    ----------
    domain : str
        Domain name to fetch WHOIS for.

    Returns
    -------
    list of str
        Extracted email addresses.
    """
    res = requests.get(f"https://api.hackertarget.com/whois/?q={domain}")
    return list(
        set(
            re.findall(
                r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", res.text
            )
        )
    )


@invoker.entry_point
def run(
    domain: sierra.Param[
        str | None,
        sierra.SierraOption(
            description="Target domain to extract WHOIS emails from.",
            mandatory="MANDATORY",
        ),
    ],
) -> None:
    if domain is None:
        result = sierra.create_error_result("Missing domain")
    else:
        emails = fetch_whois_emails(domain)
        # Fix the type issue by creating the correct structure
        tree_data: list[str | dict[str, list[str]]] = []
        for email in emails:
            tree_data.append({"📧 Email": [email]})
        result = sierra.create_tree_result(tree_data)
    print(result)


def load(client: sierra.SierraDevelopmentClient) -> None:
    client.load_invoker(invoker)
