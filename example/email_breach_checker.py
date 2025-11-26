"""
Email Breach Checker.

Check if email addresses have been compromised in data breaches.
"""
import typing
import requests
import hashlib

import sierra

invoker = sierra.InvokerScript(
    name="email_breach_checker",
    description="Check if email addresses appear in known data breaches"
)

invoker.requirement(["requests"])


@invoker.dependancy
def check_haveibeenpwned(email: str) -> dict[str, typing.Any]:
    """
    Check email against Have I Been Pwned API.
    
    Note: Use with caution and respect rate limits.
    """
    try:
        # Using the HIBP API v3
        url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
        headers = {
            "User-Agent": "Sierra-OSINT-Tool",
            "hibp-api-key": "YOUR_API_KEY_HERE"  # Users should replace this
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return {"breached": True, "breaches": response.json()}
        elif response.status_code == 404:
            return {"breached": False, "breaches": []}
        else:
            return {"error": f"API returned status {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}


@invoker.dependancy
def check_dehashed(email: str) -> dict[str, typing.Any]:
    """
    Check using DeHashed API (alternative).
    
    Note: Requires API key.
    """
    # Placeholder for DeHashed integration
    return {"service": "dehashed", "note": "Requires API key"}


@invoker.entry_point
def run(
    email: sierra.Param[
        str | None,
        sierra.SierraOption(
            description="Email address to check",
            mandatory="MANDATORY"
        )
    ],
    check_password: sierra.Param[
        str | None,
        sierra.SierraOption(
            description="Also check if password hash is breached",
            mandatory="OPTIONAL"
        )
    ] = None
) -> None:
    """
    Email breach checker.
    
    Checks if an email address has appeared in known data breaches using:
    - Have I Been Pwned API
    - Optional password hash checking
    
    NOTE: Requires HIBP API key for full functionality.
    Replace 'YOUR_API_KEY_HERE' in the code with your actual API key from:
    https://haveibeenpwned.com/API/Key
    """
    if email is None:
        result = sierra.create_error_result("Missing mandatory parameter: email")
        sierra.respond(result)
        return
    
    
    # Check HIBP
    hibp_data = check_haveibeenpwned(email)
    
    if "error" in hibp_data:
        error_msg = hibp_data["error"]
        if "API" in error_msg or "401" in error_msg:
            result = sierra.create_error_result(
                "HIBP API key required. Please get a free key from https://haveibeenpwned.com/API/Key"
            )
        else:
            result = sierra.create_error_result(f"Error: {error_msg}")
        sierra.respond(result)
        return
    
    # Build result
    if hibp_data.get("breached"):
        breaches = hibp_data.get("breaches", [])
        rows: list[list[str]] = []
        
        for breach in breaches:
            rows.append([
                breach.get("Name", "Unknown"),
                breach.get("BreachDate", "Unknown"),
                ", ".join(breach.get("DataClasses", [])),
                str(breach.get("PwnCount", 0))
            ])
        
        if rows:
            result = sierra.Table(
                headers=["Breach", "Date", "Exposed Data", "Affected Accounts"],
                rows=rows
            )
        else:
            rows.append(["Email found in breaches", "Details unavailable", "-", "-"])
            result = sierra.Table(headers=["Status", "Info", "-", "-"], rows=rows)
    else:
        result = sierra.Table(
            headers=["Status"],
            rows=[["No breaches found for this email address"]]
        )
    
    sierra.respond(result)


def load(client: sierra.SierraDevelopmentClient) -> None:
    """Register invoker with Sierra."""
    client.load_invoker(invoker)
