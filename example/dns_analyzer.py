"""
DNS Records Analyzer.

Comprehensive DNS record enumeration and analysis.
"""
import typing
import dns.resolver
import dns.reversename

import sierra

invoker = sierra.InvokerScript(
    name="dns_analyzer",
    description="Comprehensive DNS record enumeration and analysis"
)

invoker.requirement(["dnspython"])


@invoker.dependancy
def query_dns_records(domain: str, record_types: list[str]) -> dict[str, list[str]]:
    """Query multiple DNS record types."""
    resolver = dns.resolver.Resolver()
    resolver.timeout = 5
    resolver.lifetime = 5
    
    results: dict[str, list[str]] = {}
    
    for rtype in record_types:
        try:
            answers = resolver.resolve(domain, rtype)
            results[rtype] = [str(rdata) for rdata in answers]
        except Exception:
            results[rtype] = []
    
    return results


@invoker.dependancy
def reverse_dns_lookup(ip: str) -> str:
    """Perform reverse DNS lookup."""
    try:
        addr = dns.reversename.from_address(ip)
        answers = dns.resolver.resolve(addr, 'PTR')
        return str(answers[0])
    except Exception:
        return "N/A"


@invoker.entry_point
def run(
    domain: sierra.Param[
        str | None,
        sierra.SierraOption(
            description="Domain to analyze",
            mandatory="MANDATORY"
        )
    ],
    record_types: sierra.Param[
        str | None,
        sierra.SierraOption(
            description="Comma-separated record types (default AAAAAMXNSTXTSOACNAME)",
            mandatory="OPTIONAL"
        )
    ] = None
) -> None:
    """
    DNS record analyzer.
    
    Enumerates and displays DNS records:
    - A (IPv4 addresses)
    - AAAA (IPv6 addresses)
    - MX (Mail servers)
    - NS (Nameservers)
    - TXT (Text records)
    - SOA (Start of Authority)
    - CNAME (Canonical names)
    """
    if domain is None:
        result = sierra.create_error_result("Missing mandatory parameter: domain")
        sierra.respond(result)
        return
    
    # Parse record types
    if record_types:
        types = [t.strip().upper() for t in record_types.split(",")]
    else:
        types = ["A", "AAAA", "MX", "NS", "TXT", "SOA", "CNAME"]
    
    
    # Query all record types
    dns_data = query_dns_records(domain, types)
    
    # Build result table
    rows: list[list[str]] = []
    
    for rtype, records in dns_data.items():
        if records:
            for record in records:
                # For A records, also do reverse lookup
                if rtype == "A" and "." in str(record):
                    ptr = reverse_dns_lookup(str(record))
                    rows.append([rtype, str(record), ptr])
                else:
                    rows.append([rtype, str(record), "-"])
        else:
            rows.append([rtype, "No records found", "-"])
    
    if rows:
        result = sierra.Table(
            headers=["Record Type", "Value", "Reverse DNS"],
            rows=rows
        )
    else:
        result = sierra.create_error_result(f"No DNS records found for {domain}")
    
    sierra.respond(result)


def load(client: sierra.SierraDevelopmentClient) -> None:
    """Register invoker with Sierra."""
    client.load_invoker(invoker)
