"""
Advanced Subdomain Enumeration Tool.

Combines multiple techniques for comprehensive subdomain discovery.
"""
import typing
import requests
import dns.resolver
import ssl
import socket

import sierra

invoker = sierra.InvokerScript(
    name="subdomain_enumerator",
    description="Advanced subdomain discovery using multiple techniques"
)

invoker.requirement(["requests", "dnspython"])


@invoker.dependancy
def check_crtsh(domain: str) -> set[str]:
    """Query crt.sh certificate transparency logs."""
    try:
        url = f"https://crt.sh/?q=%.{domain}&output=json"
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            data = response.json()
            subdomains = set()
            for entry in data:
                name = entry.get("name_value", "")
                for subdomain in name.split("\n"):
                    subdomain = subdomain.strip().replace("*.", "")
                    if subdomain.endswith(domain) and subdomain != domain:
                        subdomains.add(subdomain)
            return subdomains
    except Exception:
        pass
    return set()


@invoker.dependancy
def check_hackertarget(domain: str) -> set[str]:
    """Query HackerTarget API for subdomains."""
    try:
        url = f"https://api.hackertarget.com/hostsearch/?q={domain}"
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            subdomains = set()
            for line in response.text.split("\n"):
                if "," in line:
                    subdomain = line.split(",")[0].strip()
                    if subdomain and subdomain.endswith(domain):
                        subdomains.add(subdomain)
            return subdomains
    except Exception:
        pass
    return set()


@invoker.dependancy
def bruteforce_common(domain: str, wordlist: list[str]) -> set[str]:
    """Brute force common subdomain names."""
    subdomains = set()
    resolver = dns.resolver.Resolver()
    resolver.timeout = 2
    resolver.lifetime = 2
    
    for word in wordlist:
        subdomain = f"{word}.{domain}"
        try:
            resolver.resolve(subdomain, 'A')
            subdomains.add(subdomain)
        except Exception:
            pass
    
    return subdomains


@invoker.entry_point
def run(
    domain: sierra.Param[
        str | None,
        sierra.SierraOption(
            description="Target domain for subdomain enumeration",
            mandatory="MANDATORY"
        )
    ],
    wordlist: sierra.Param[
        str | None,
        sierra.SierraOption(
            description="Use bruteforce with common wordlist (slow)",
            mandatory="OPTIONAL"
        )
    ] = None
) -> None:
    """
    Advanced subdomain enumeration tool.
    
    Combines multiple techniques:
    - Certificate Transparency (crt.sh)
    - HackerTarget API
    - Optional DNS bruteforce
    """
    if domain is None:
        result = sierra.create_error_result("Missing mandatory parameter: domain")
        sierra.respond(result)
        return
    
    
    # Collect subdomains from all sources
    all_subdomains: set[str] = set()
    
    # CRT.SH
    crtsh_subs = check_crtsh(domain)
    all_subdomains.update(crtsh_subs)
    
    # HackerTarget
    ht_subs = check_hackertarget(domain)
    all_subdomains.update(ht_subs)
    
    # Optional bruteforce
    if wordlist:
        common_names = [
            "www", "mail", "remote", "blog", "webmail", "server",
            "ns1", "ns2", "smtp", "secure", "vpn", "admin",
            "portal", "ftp", "api", "dev", "staging", "test"
        ]
        brute_subs = bruteforce_common(domain, common_names)
        all_subdomains.update(brute_subs)
    
    # Build result table
    if all_subdomains:
        rows = [[subdomain] for subdomain in sorted(all_subdomains)]
        result = sierra.Table(
            headers=["Subdomain"],
            rows=rows
        )
    else:
        result = sierra.create_error_result(f"No subdomains found for {domain}")
    
    sierra.respond(result)


def load(client: sierra.SierraDevelopmentClient) -> None:
    """Register invoker with Sierra."""
    client.load_invoker(invoker)
