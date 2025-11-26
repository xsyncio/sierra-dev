"""
Port Scanner Tool.

Fast TCP port scanner with service detection.
"""
import typing
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed

import sierra

invoker = sierra.InvokerScript(
    name="port_scanner",
    description="Fast TCP port scanner with service detection"
)


@invoker.dependancy
def scan_port(ip: str, port: int, timeout: float = 1.0) -> tuple[int, str, str]:
    """Scan a single port."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        sock.close()
        
        if result == 0:
            service = get_service_name(port)
            return port, "Open", service
        else:
            return port, "Closed", "-"
    except Exception:
        return port, "Error", "-"


@invoker.dependancy
def get_service_name(port: int) -> str:
    """Get common service name for a port."""
    common_ports = {
        20: "FTP Data",
        21: "FTP Control",
        22: "SSH",
        23: "Telnet",
        25: "SMTP",
        53: "DNS",
        80: "HTTP",
        110: "POP3",
        143: "IMAP",
        443: "HTTPS",
        445: "SMB",
        3306: "MySQL",
        3389: "RDP",
        5432: "PostgreSQL",
        5900: "VNC",
        6379: "Redis",
        8080: "HTTP Proxy",
        8443: "HTTPS Alt",
        27017: "MongoDB"
    }
    return common_ports.get(port, "Unknown")


@invoker.entry_point
def run(
    target: sierra.Param[
        str | None,
        sierra.SierraOption(
            description="Target IP address or hostname to scan",
            mandatory="MANDATORY"
        )
    ],
    ports: sierra.Param[
        str | None,
        sierra.SierraOption(
            description="Ports to scan (e.g. 804438080 or common or 1-1000)",
            mandatory="OPTIONAL"
        )
    ] = "common",
    threads: sierra.Param[
        int | None,
        sierra.SierraOption(
            description="Number of concurrent threads (default 50)",
            mandatory="OPTIONAL"
        )
    ] = 50
) -> None:
    """
    TCP port scanner.
    
    Scans specified ports on a target:
    - Common ports (default): Top 20 most common ports
    - Specific ports: Comma-separated list (e.g., 80,443,8080)
    - Port range: Hyphenated range (e.g., 1-1000)
    
    Features:
    - Concurrent scanning for speed
    - Service name detection
    - Customizable thread count
    """
    if target is None:
        result = sierra.create_error_result("Missing mandatory parameter: target")
        sierra.respond(result)
        return
    
    # Determine ports to scan
    if ports == "common":
        port_list = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 3306, 3389, 5432, 5900, 6379, 8080, 8443, 27017]
    elif "-" in str(ports):
        # Port range
        start, end = map(int, str(ports).split("-"))
        port_list = list(range(start, end + 1))
    else:
        # Comma-separated
        port_list = [int(p.strip()) for p in str(ports).split(",")]
    
    
    # Scan ports concurrently
    open_ports: list[tuple[int, str, str]] = []
    
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {executor.submit(scan_port, target, port): port for port in port_list}
        
        completed = 0
        for future in as_completed(futures):
            port, status, service = future.result()
            if status == "Open":
                open_ports.append((port, status, service))
            
            completed += 1
            # Build result
    if open_ports:
        # Sort by port number
        open_ports.sort(key=lambda x: x[0])
        rows = [[str(port), status, service] for port, status, service in open_ports]
        
        result = sierra.Table(
            headers=["Port", "Status", "Service"],
            rows=rows
        )
        
    else:
        result = sierra.Table(
            headers=["Status"],
            rows=[["No open ports found"]]
        )
    
    sierra.respond(result)


def load(client: sierra.SierraDevelopmentClient) -> None:
    """Register invoker with Sierra."""
    client.load_invoker(invoker)
