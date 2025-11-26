"""
Comprehensive WHOIS Lookup Tool.

Query WHOIS information for domains and IPs.
"""
import typing
import requests
import re
from datetime import datetime

import sierra

invoker = sierra.InvokerScript(
    name="whois_lookup",
    description="Comprehensive WHOIS information retrieval"
)

invoker.requirement(["requests"])


@invoker.dependancy
def query_whois_api(target: str) -> dict[str, typing.Any]:
    """Query WHOIS data using IP  API."""
    try:
        # Using ipapi.co for comprehensive WHOIS data
        if re.match(r'^\d+\.\d+\.\d+\.\d+$', target):
            # IP address
            url = f"https://ipapi.co/{target}/json/"
        else:
            # Domain name - use whoisxmlapi free tier alternative
            url = f"https://www.whoisxmlapi.com/whoisserver/WhoisService?apiKey=at_FREE&domainName={target}&outputFormat=JSON"
            
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        return {"error": str(e)}
    return {}


@invoker.dependancy
def parse_whois_data(data: dict[str, typing.Any], target: str) -> list[list[str]]:
    """Parse WHOIS data into table rows."""
    rows: list[list[str]] = []
    
    # Check if IP or domain
    if re.match(r'^\d+\.\d+\.\d+\.\d+$', target):
        # IP WHOIS data
        rows.append(["IP Address", data.get("ip", target)])
        rows.append(["Network", data.get("network", "N/A")])
        rows.append(["Version", data.get("version", "N/A")])
        rows.append(["City", data.get("city", "N/A")])
        rows.append(["Region", data.get("region", "N/A")])
        rows.append(["Country", f"{data.get('country_name', 'N/A')} ({data.get('country', 'N/A')})"])
        rows.append(["Postal Code", data.get("postal", "N/A")])
        rows.append(["Coordinates", f"{data.get('latitude', 'N/A')}, {data.get('longitude', 'N/A')}"])
        rows.append(["Timezone", data.get("timezone", "N/A")])
        rows.append(["ASN", data.get("asn", "N/A")])
        rows.append(["Organization", data.get("org", "N/A")])
    else:
        # Domain WHOIS data
        whois_record = data.get("WhoisRecord", {})
        rows.append(["Domain", target])
        rows.append(["Registrar", whois_record.get("registrarName", "N/A")])
        rows.append(["Created Date", whois_record.get("createdDate", "N/A")])
        rows.append(["Updated Date", whois_record.get("updatedDate", "N/A")])
        rows.append(["Expires Date", whois_record.get("expiresDate", "N/A")])
        
        # Registrant info
        registrant = whois_record.get("registrant", {})
        rows.append(["Registrant Name", registrant.get("name", "N/A")])
        rows.append(["Registrant Org", registrant.get("organization", "N/A")])
        rows.append(["Registrant Email", registrant.get("email", "N/A")])
        
        # Nameservers
        nameservers = whois_record.get("nameServers", {})
        if isinstance(nameservers, dict):
            ns_list = nameservers.get("hostNames", [])
            if ns_list:
                rows.append(["Nameservers", ", ".join(ns_list)])
    
    return rows


@invoker.entry_point
def run(
    target: sierra.Param[
        str | None,
        sierra.SierraOption(
            description="Domain name or IP address to lookup",
            mandatory="MANDATORY"
        )
    ]
) -> None:
    """
    WHOIS information lookup.
    
    Retrieves comprehensive WHOIS data for:
    - Domain names (registration, expiry, nameservers)
    - IP addresses (geolocation, ASN, organization)
    """
    if target is None:
        result = sierra.create_error_result("Missing mandatory parameter: target")
        sierra.respond(result)
        return
    
    
    # Query WHOIS data
    data = query_whois_api(target)
    
    if not data or "error" in data:
        result = sierra.create_error_result(f"Failed to retrieve WHOIS data for {target}")
        sierra.respond(result)
        return
    
    # Parse into table
    rows = parse_whois_data(data, target)
    
    if rows:
        result = sierra.Table(
            headers=["Field", "Value"],
            rows=rows
        )
        sierra.respond(result)
    else:
        result = sierra.create_error_result("No WHOIS data available")
        sierra.respond(result)


def load(client: sierra.SierraDevelopmentClient) -> None:
    """Register invoker with Sierra."""
    client.load_invoker(invoker)
