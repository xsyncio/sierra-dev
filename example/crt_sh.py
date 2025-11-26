import typing

import requests

import sierra

# Define the InvokerScript for crt.sh subdomain and email lookup
invoker = sierra.InvokerScript(
    name="crtsh_extended",
    description="Lookup subdomains and email addresses via Certificate Search (crt.sh)",
)

invoker.requirement(["requests"])


@invoker.dependancy
def get_crtsh_records(domain: str) -> tuple[list[str], list[str]]:
    """
    Fetch certificate entries from crt.sh, extract and categorize subdomains and emails.

    Parameters
    ----------
    domain : str
        The base domain to query on crt.sh.

    Returns
    -------
    tuple[list[str], list[str]]
        A tuple where the first element is a list of unique subdomains (excluding the base domain),
        and the second element is a list of discovered email addresses.
    """
    response = requests.get(f"https://crt.sh/?q={domain}&output=json")
    data: list[dict[str, typing.Any]] = response.json()  # type: ignore
    # Collect all entries
    records: list[str] = []
    for item in data:
        common = item.get("common_name")
        if common:
            records.append(common.lower())
        name_values = item.get("name_value", "").split("\n")
        for nv in name_values:
            records.append(nv.lower())

    # Deduplicate
    records = list(set(records))

    subdomains: list[str] = []
    emails: list[str] = []

    for rec in records:
        rec_clean = rec.replace("*.", "")
        # Skip entries not containing the base domain or equal to it
        if rec_clean == domain or domain not in rec_clean:
            continue
        if "@" in rec_clean:
            emails.append(rec_clean)
        else:
            subdomains.append(rec_clean)

    return subdomains, emails


@invoker.entry_point
def run(
    domain: sierra.Param[
        str | None,
        sierra.SierraOption(
            description="Domain name to lookup via crt.sh.",
            mandatory="MANDATORY",
        ),
    ],
) -> None:
    """
    Entry point for the extended crtsh invoker.

    Retrieves subdomains and emails by querying crt.sh and outputs a tree result for subdomains.
    """
    if domain is None:
        result = sierra.create_error_result(
            "Missing mandatory parameter: domain"
        )
    else:
        subdomains, emails = get_crtsh_records(domain)
        # Fix the type issue by creating the correct structure
        tree_data: list[str | dict[str, list[str]]] = []

        # Add subdomains section
        if subdomains:
            tree_data.append("🌐 Subdomains")
            for subdomain in subdomains:
                tree_data.append({"Subdomain": [subdomain]})

        # Add emails section
        if emails:
            tree_data.append("📧 Email Addresses")
            for email in emails:
                tree_data.append({"Email": [email]})

        # If no data found, add a message
        if not subdomains and not emails:
            tree_data.append("No subdomains or emails found")

        result = sierra.create_tree_result(tree_data)
    sierra.respond(result)


def load(client: sierra.SierraDevelopmentClient) -> None:
    """
    Load hook for Sierra plugin loader.

    Registers the extended crtsh invoker with the Sierra CLI/GUI runners.
    """
    client.load_invoker(invoker)
