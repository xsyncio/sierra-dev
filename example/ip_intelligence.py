"""
IP Geolocation and Network Information Tool.

Comprehensive IP address intelligence gathering.
"""
import typing
import requests
import socket

import sierra

invoker = sierra.InvokerScript(
    name="ip_intelligence",
    description="Comprehensive IP geolocation and network intelligence"
)

invoker.requirement(["requests"])


@invoker.dependancy
def get_ip_info(ip: str) -> dict[str, typing.Any]:
    """Query comprehensive IP information."""
    try:
        # Using ipapi.co for comprehensive data
        response = requests.get(f"https://ipapi.co/{ip}/json/", timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return {}


@invoker.dependancy
def check_vpn_proxy(ip: str) -> dict[str, bool]:
    """Check if IP is VPN/proxy using proxycheck.io."""
    try:
        response = requests.get(f"https://proxycheck.io/v2/{ip}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            ip_data = data.get(ip, {})
            return {
                "is_proxy": ip_data.get("proxy", "no") == "yes",
                "is_vpn": ip_data.get("type", "").lower() == "vpn"
            }
    except Exception:
        pass
    return {"is_proxy": False, "is_vpn": False}


@invoker.dependancy
def reverse_dns(ip: str) -> str:
    """Perform reverse DNS lookup."""
    try:
        hostname, _, _ = socket.gethostbyaddr(ip)
        return hostname
    except Exception:
        return "N/A"


@invoker.entry_point
def run(
    ip: sierra.Param[
        str | None,
        sierra.SierraOption(
            description="IP address to analyze",
            mandatory="MANDATORY"
        )
    ]
) -> None:
    """
    IP intelligence gathering tool.
    
    Provides comprehensive information about an IP address:
    - Geolocation (city, region, country)
    - Network information (ASN, organization)
    - VPN/Proxy detection
    - Reverse DNS
    - Timezone and coordinates
    """
    if ip is None:
        result = sierra.create_error_result("Missing mandatory parameter: ip")
        sierra.respond(result)
        return
    
    
    # Get IP info
    ip_data = get_ip_info(ip)
    
    if not ip_data:
        result = sierra.create_error_result(f"Failed to retrieve information for {ip}")
        sierra.respond(result)
        return
    
    # Check VPN/Proxy
    vpn_check = check_vpn_proxy(ip)
    
    # Reverse DNS
    hostname = reverse_dns(ip)
    
    # Build comprehensive result table
    rows: list[list[str]] = []
    
    # Basic info
    rows.append(["IP Address", ip])
    rows.append(["Hostname", hostname])
    rows.append(["", ""])  # Separator
    
    # Geolocation
    rows.append(["🌍 LOCATION", ""])
    rows.append(["City", ip_data.get("city", "N/A")])
    rows.append(["Region", ip_data.get("region", "N/A")])
    rows.append(["Country", f"{ip_data.get('country_name', 'N/A')} ({ip_data.get('country_code', 'N/A')})"])
    rows.append(["Postal Code", ip_data.get("postal", "N/A")])
    rows.append(["Coordinates", f"{ip_data.get('latitude', 'N/A')}, {ip_data.get('longitude', 'N/A')}"])
    rows.append(["Timezone", ip_data.get("timezone", "N/A")])
    rows.append(["", ""])
    
    # Network info
    rows.append(["🌐 NETWORK", ""])
    rows.append(["ASN", ip_data.get("asn", "N/A")])
    rows.append(["Organization", ip_data.get("org", "N/A")])
    rows.append(["ISP", ip_data.get("org", "N/A")])  # Same as org usually
    rows.append(["", ""])
    
    # Security
    rows.append(["🔒 SECURITY", ""])
    rows.append(["VPN Detected", "Yes" if vpn_check.get("is_vpn") else "No"])
    rows.append(["Proxy Detected", "Yes" if vpn_check.get("is_proxy") else "No"])
    rows.append(["", ""])
    
    # Additional
    rows.append(["📊 ADDITIONAL", ""])
    rows.append(["Currency", ip_data.get("currency", "N/A")])
    rows.append(["Languages", ip_data.get("languages", "N/A")])
    
    result = sierra.Table(
        headers=["Field", "Value"],
        rows=rows
    )
    
    sierra.respond(result)


def load(client: sierra.SierraDevelopmentClient) -> None:
    """Register invoker with Sierra."""
    client.load_invoker(invoker)
