"""
SSL/TLS Certificate Information Tool.

Analyze SSL/TLS certificates for security and validity information.
"""
import typing
import ssl
import socket
from datetime import datetime
from urllib.parse import urlparse

import sierra

invoker = sierra.InvokerScript(
    name="ssl_cert_analyzer",
    description="Analyze SSL/TLS certificate information"
)


@invoker.dependancy
def get_ssl_certificate(hostname: str, port: int = 443) -> dict[str, typing.Any]:
    """Retrieve SSL certificate from a hostname."""
    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                return cert
    except Exception as e:
        return {"error": str(e)}


@invoker.dependancy
def parse_certificate(cert: dict[str, typing.Any]) -> list[list[str]]:
    """Parse certificate data into readable format."""
    rows: list[list[str]] = []
    
    if "error" in cert:
        rows.append(["Error", cert["error"]])
        return rows
    
    # Subject info
    subject = dict(x[0] for x in cert.get("subject", []))
    rows.append(["Common Name (CN)", subject.get("commonName", "N/A")])
    rows.append(["Organization (O)", subject.get("organizationName", "N/A")])
    rows.append(["Organizational Unit (OU)", subject.get("organizationalUnitName", "N/A")])
    rows.append(["Country (C)", subject.get("countryName", "N/A")])
    rows.append(["", ""])
    
    # Issuer info
    issuer = dict(x[0] for x in cert.get("issuer", []))
    rows.append(["🔒 ISSUER", ""])
    rows.append(["Issuer Name", issuer.get("commonName", "N/A")])
    rows.append(["Issuer Organization", issuer.get("organizationName", "N/A")])
    rows.append(["", ""])
    
    # Validity
    rows.append(["📅 VALIDITY", ""])
    not_before = cert.get("notBefore", "")
    not_after = cert.get("notAfter", "")
    rows.append(["Valid From", not_before])
    rows.append(["Valid Until", not_after])
    
    # Check if expired
    if not_after:
        try:
            expiry_date = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z")
            is_expired = expiry_date < datetime.now()
            days_left = (expiry_date - datetime.now()).days
            
            if is_expired:
                rows.append(["Status", "⚠️ EXPIRED"])
            elif days_left < 30:
                rows.append(["Status", f"⚠️ Expiring soon ({days_left} days)"])
            else:
                rows.append(["Status", f"✅ Valid ({days_left} days remaining)"])
        except Exception:
            rows.append(["Status", "Unknown"])
    
    rows.append(["", ""])
    
    # Subject Alternative Names
    san = cert.get("subjectAltName", [])
    if san:
        san_list = [name[1] for name in san if name[0] == "DNS"]
        rows.append(["📝 ALTERNATIVE NAMES", ""])
        rows.append(["DNS Names", ", ".join(san_list[:5])])  # First 5
        if len(san_list) > 5:
            rows.append(["", f"... and {len(san_list) - 5} more"])
    
    rows.append(["", ""])
    
    # Technical details
    rows.append(["🔧 TECHNICAL", ""])
    rows.append(["Serial Number", cert.get("serialNumber", "N/A")])
    rows.append(["Version", str(cert.get("version", "N/A"))])
    
    return rows


@invoker.entry_point
def run(
    hostname: sierra.Param[
        str | None,
        sierra.SierraOption(
            description="Hostname to analyze SSL certificate",
            mandatory="MANDATORY"
        )
    ],
    port: sierra.Param[
        int | None,
        sierra.SierraOption(
            description="Port number (default 443)",
            mandatory="OPTIONAL"
        )
    ] = 443
) -> None:
    """
    SSL/TLS certificate analyzer.
    
    Retrieves and analyzes SSL certificate information:
    - Subject and issuer details
    - Validity period and expiration
    - Alternative DNS names
    - Serial number and version
    - Expiration warnings
    """
    if hostname is None:
        result = sierra.create_error_result("Missing mandatory parameter: hostname")
        sierra.respond(result)
        return
    
    # Clean hostname (remove https://, etc.)
    if "://" in hostname:
        hostname = urlparse(hostname).netloc or hostname
    
    port_num = port if port is not None else 443
    
    
    # Get certificate
    cert = get_ssl_certificate(hostname, port_num)
    
    # Parse certificate
    rows = parse_certificate(cert)
    
    if rows:
        result = sierra.Table(
            headers=["Field", "Value"],
            rows=rows
        )
    else:
        result = sierra.create_error_result("Failed to retrieve certificate")
    
    sierra.respond(result)


def load(client: sierra.SierraDevelopmentClient) -> None:
    """Register invoker with Sierra."""
    client.load_invoker(invoker)
