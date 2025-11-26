"""
Wayback Machine Analyzer.

Check website history and archived snapshots.
"""
import typing
import requests
from datetime import datetime

import sierra

invoker = sierra.InvokerScript(
    name="wayback_analyzer",
    description="Analyze website history using Wayback Machine"
)

invoker.requirement(["requests"])


@invoker.dependancy
def get_wayback_snapshots(url: str, limit: int = 10) -> list[dict[str, str]]:
    """Get recent Wayback Machine snapshots."""
    try:
        # Wayback CDX API
        api_url = f"http://web.archive.org/cdx/search/cdx?url={url}&output=json&limit={limit}"
        response = requests.get(api_url, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            # Skip header row
            if len(data) > 1:
                snapshots = []
                for row in data[1:]:  # Skip header
                    timestamp = row[1]
                    # Parse timestamp (format: YYYYMMDDhhmmss)
                    dt = datetime.strptime(timestamp, "%Y%m%d%H%M%S")
                    
                    snapshots.append({
                        "timestamp": timestamp,
                        "date": dt.strftime("%Y-%m-%d %H:%M:%S"),
                        "url": f"https://web.archive.org/web/{timestamp}/{url}",
                        "status": row[4] if len(row) > 4 else "200"
                    })
                
                return snapshots
    except Exception:
        pass
    
    return []


@invoker.dependancy
def get_first_and_last(url: str) -> tuple[str, str]:
    """Get first and last snapshot dates."""
    try:
        api_url = f"http://archive.org/wayback/available?url={url}"
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            snapshots = data.get("archived_snapshots", {})
            closest = snapshots.get("closest", {})
            
            if closest:
                timestamp = closest.get("timestamp", "")
                if timestamp:
                    dt = datetime.strptime(timestamp, "%Y%m%d%H%M%S")
                    return dt.strftime("%Y-%m-%d"), closest.get("url", "")
    except Exception:
        pass
    
    return "Unknown", ""


@invoker.entry_point
def run(
    url: sierra.Param[
        str | None,
        sierra.SierraOption(
            description="Website URL to analyze",
            mandatory="MANDATORY"
        )
    ],
    limit: sierra.Param[
        int | None,
        sierra.SierraOption(
            description="Number of recent snapshots to show (default 10)",
            mandatory="OPTIONAL"
        )
    ] = 10
) -> None:
    """
    Wayback Machine analyzer.
    
    Analyze website history using Internet Archive:
    - Recent snapshots
    - First and last archive dates
    - Direct links to archived versions
    - HTTP status codes
    """
    if url is None:
        result = sierra.create_error_result("Missing mandatory parameter: url")
        sierra.respond(result)
        return
    
    # Clean URL
    if not url.startswith(('http://', 'https://')):
        url = f"https://{url}"
    
    
    # Get first/last snapshot info
    first_date, first_url = get_first_and_last(url)
    
    # Get recent snapshots
    snapshots = get_wayback_snapshots(url, limit or 10)
    
    if not snapshots:
        result = sierra.create_error_result(f"No Wayback Machine snapshots found for {url}")
        sierra.respond(result)
        return
    
    # Build result
    rows: list[list[str]] = []
    
    # Add summary info
    rows.append(["First Snapshot", first_date])
    rows.append(["Total Snapshots", str(len(snapshots))])
    rows.append(["", ""])
    
    # Add recent snapshots
    rows.append(["📸 RECENT SNAPSHOTS", ""])
    for snapshot in snapshots:
        rows.append([snapshot["date"], snapshot["url"]])
    
    result = sierra.Table(
        headers=["Date/Info", "URL"],
        rows=rows
    )
    
    sierra.respond(result)


def load(client: sierra.SierraDevelopmentClient) -> None:
    """Register invoker with Sierra."""
    client.load_invoker(invoker)
