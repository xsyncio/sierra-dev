import re
from urllib.parse import quote

import requests

import sierra

invoker = sierra.InvokerScript(
    name="digital_footprint_analyzer",
    description="Advanced OSINT tool that analyzes digital footprints across multiple sources including breach data social media and domain associations",
)

invoker.requirement(["requests"])


@invoker.dependancy
def check_haveibeenpwned(email: str) -> list[str]:
    """Check if email appears in known data breaches via HaveIBeenPwned API."""
    try:
        # Using the public API (rate limited)
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; OSINT-Tool/1.0)",
        }
        url = (
            f"https://haveibeenpwned.com/api/v3/breachedaccount/{quote(email)}"
        )
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            breaches = response.json()
            return [breach.get("Name", "Unknown") for breach in breaches]
        elif response.status_code == 404:
            return []  # No breaches found
        else:
            return ["API_ERROR"]
    except Exception:
        return ["CONNECTION_ERROR"]


@invoker.dependancy
def search_social_mentions(query: str) -> list[dict[str, str]]:
    """Search for social media mentions using multiple sources."""
    mentions: list[dict[str, str]] = []

    # Search GitHub for user profiles and repositories
    try:
        github_url = f"https://api.github.com/search/users?q={quote(query)}"
        headers = {"User-Agent": "OSINT-Tool/1.0"}
        response = requests.get(github_url, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            for user in data.get("items", [])[:5]:  # Limit to top 5
                mentions.append(
                    {
                        "platform": "GitHub",
                        "username": user.get("login", ""),
                        "profile_url": user.get("html_url", ""),
                        "type": "Profile",
                    }
                )
    except Exception:
        pass

    # Search for email in pastebins and leaks (using a search engine approach)
    try:
        search_query = (
            f'"{query}" site:pastebin.com OR site:paste.ee OR site:ghostbin.co'
        )
        # Note: This would need a proper search API in real implementation
        # For demonstration, we'll simulate some results
        if "@" in query:  # If it's an email
            mentions.append(
                {
                    "platform": "Pastebin",
                    "username": "N/A",
                    "profile_url": f"https://www.google.com/search?q={quote(search_query)}",
                    "type": "Search Results",
                }
            )
    except Exception:
        pass

    return mentions


@invoker.dependancy
def find_associated_domains(email: str) -> list[str]:
    """Find domains associated with an email using various techniques."""
    domains: list[str] = []

    if "@" not in email:
        return domains

    domain = email.split("@")[1]
    domains.append(domain)

    # Try to find related domains using certificate transparency logs
    try:
        # Search for certificates containing the domain
        ct_url = f"https://crt.sh/?q={quote(domain)}&output=json"
        response = requests.get(ct_url, timeout=15)

        if response.status_code == 200:
            certs = response.json()
            for cert in certs[:20]:  # Limit results
                common_name = cert.get("common_name", "")
                if common_name and common_name != domain:
                    # Extract domain from common name
                    clean_domain = common_name.replace("*.", "").lower()
                    if "." in clean_domain and clean_domain not in domains:
                        domains.append(clean_domain)
    except Exception:
        pass

    return list(set(domains))


@invoker.dependancy
def generate_email_variants(base_email: str) -> list[str]:
    """Generate common email variants for broader searching."""
    if "@" not in base_email:
        return [base_email]

    local, domain = base_email.split("@", 1)
    variants = [base_email]

    # Common variations
    variations = [
        local.replace(".", ""),
        local.replace("_", "."),
        local.replace("-", "."),
        local + "1",
        local + "123",
        "admin@" + domain,
        "info@" + domain,
        "contact@" + domain,
    ]

    for var in variations:
        if "@" not in var:
            variants.append(var + "@" + domain)
        else:
            variants.append(var)

    return list(set(variants))


@invoker.dependancy
def check_email_reputation(email: str) -> dict[str, str]:
    """Check email reputation and validity indicators."""
    reputation = {
        "disposable": "Unknown",
        "mx_valid": "Unknown",
        "format_valid": "Valid"
        if re.match(r"^[^@]+@[^@]+\.[^@]+$", email)
        else "Invalid",
    }

    if "@" not in email:
        return reputation

    domain = email.split("@")[1]

    # Check against known disposable email domains
    disposable_domains = [
        "10minutemail.com",
        "guerrillamail.com",
        "mailinator.com",
        "tempmail.org",
        "yopmail.com",
        "sharklasers.com",
    ]

    reputation["disposable"] = "Yes" if domain in disposable_domains else "No"

    return reputation


@invoker.entry_point
def run(
    target: sierra.Param[
        str | None,
        sierra.SierraOption(
            description="Email address or username to analyze for digital footprint",
            mandatory="MANDATORY",
        ),
    ],
) -> None:
    """
    Entry point for digital footprint analysis.

    Performs comprehensive OSINT analysis including breach checking,
    social media presence, domain associations, and reputation analysis.
    """
    if target is None:
        result = sierra.create_error_result("Missing target parameter")
        sierra.respond(result)
        return

    tree_data: list[str | dict[str, list[str]]] = []

    # Basic target info
    tree_data.append("🎯 Target Analysis")
    tree_data.append({"Target": [target]})

    # Initialize breaches variable to avoid unbound variable error
    breaches: list[str] = []

    # Email validation and reputation (if email)
    if "@" in target:
        tree_data.append("📊 Email Reputation")
        reputation = check_email_reputation(target)
        for key, value in reputation.items():
            tree_data.append({key.replace("_", " ").title(): [value]})

        # Check for data breaches
        tree_data.append("🔓 Breach Analysis")
        breaches = check_haveibeenpwned(target)
        if breaches:
            if "API_ERROR" in breaches or "CONNECTION_ERROR" in breaches:
                tree_data.append({"Status": ["Unable to check breaches"]})
            else:
                for breach in breaches[:10]:  # Limit to 10 breaches
                    tree_data.append({"Found in": [breach]})
        else:
            tree_data.append({"Status": ["No breaches found (Good news!)"]})

        # Generate email variants for broader search
        tree_data.append("📧 Email Variants")
        variants = generate_email_variants(target)
        for variant in variants[:8]:  # Limit variants
            if variant != target:
                tree_data.append({"Variant": [variant]})

        # Find associated domains
        tree_data.append("🌐 Associated Domains")
        domains = find_associated_domains(target)
        for domain in domains[:10]:  # Limit domains
            tree_data.append({"Domain": [domain]})

    # Social media and online presence
    tree_data.append("📱 Social Media Presence")
    mentions = search_social_mentions(target)
    if mentions:
        for mention in mentions:
            platform_info = f"{mention['platform']} - {mention['type']}"
            if mention["username"]:
                platform_info += f" ({mention['username']})"
            tree_data.append({platform_info: [mention["profile_url"]]})
    else:
        tree_data.append(
            {"Status": ["No obvious social media presence found"]}
        )

    # Additional OSINT suggestions
    tree_data.append("🔍 Suggested Manual Checks")
    suggestions = [
        "Search on Pipl.com for people search",
        "Check LinkedIn with advanced search operators",
        "Search on Shodan.io if target has associated domains",
        "Check Wayback Machine for historical data",
        "Search on specialized forums and communities",
        "Check professional networking sites",
        "Look for academic papers or publications",
    ]

    for suggestion in suggestions:
        tree_data.append({"Manual Check": [suggestion]})

    # Privacy score calculation
    tree_data.append("🛡️ Privacy Assessment")
    privacy_score = 100

    if (
        breaches
        and "API_ERROR" not in breaches
        and "CONNECTION_ERROR" not in breaches
    ):
        privacy_score -= len(breaches) * 15

    if mentions:
        privacy_score -= len(mentions) * 10

    if "@" in target and check_email_reputation(target)["disposable"] == "No":
        privacy_score -= 5  # Real email domains are less private

    privacy_score = max(0, privacy_score)

    if privacy_score >= 80:
        assessment = "Excellent - Low digital footprint"
    elif privacy_score >= 60:
        assessment = "Good - Moderate digital footprint"
    elif privacy_score >= 40:
        assessment = "Fair - Significant digital presence"
    else:
        assessment = "Poor - High digital exposure"

    tree_data.append(
        {"Privacy Score": [f"{privacy_score}/100 - {assessment}"]}
    )

    result = sierra.create_tree_result(tree_data)
    sierra.respond(result)


def load(client: sierra.SierraDevelopmentClient) -> None:
    """Load hook for Sierra plugin loader."""
    client.load_invoker(invoker)
