"""
Username Availability Checker Across Platforms.

Check username availability on multiple social media and web platforms.
"""
import typing
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

import sierra

invoker = sierra.InvokerScript(
    name="username_checker",
    description="Check username availability across multiple platforms"
)

invoker.requirement(["requests"])


@invoker.dependancy
def check_platform(platform: str, username: str) -> tuple[str, str, str]:
    """Check if username exists on a platform."""
    platforms_config = {
        "github": {
            "url": f"https://github.com/{username}",
            "exists_code": 200
        },
        "twitter": {
            "url": f"https://twitter.com/{username}",
            "exists_code": 200
        },
        "instagram": {
            "url": f"https://www.instagram.com/{username}/",
            "exists_code": 200
        },
        "reddit": {
            "url": f"https://www.reddit.com/user/{username}",
            "exists_code": 200
        },
        "linkedin": {
            "url": f"https://www.linkedin.com/in/{username}",
            "exists_code": 200
        },
        "youtube": {
            "url": f"https://www.youtube.com/@{username}",
            "exists_code": 200
        },
        "medium": {
            "url": f"https://medium.com/@{username}",
            "exists_code": 200
        },
        "pinterest": {
            "url": f"https://www.pinterest.com/{username}/",
            "exists_code": 200
        },
        "tumblr": {
            "url": f"https://{username}.tumblr.com",
            "exists_code": 200
        },
        "twitch": {
            "url": f"https://www.twitch.tv/{username}",
            "exists_code": 200
        }
    }
    
    config = platforms_config.get(platform.lower())
    if not config:
        return platform, "Unknown", "-"
    
    try:
        response = requests.get(
            config["url"],
            timeout=10,
            allow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        
        if response.status_code == config["exists_code"]:
            return platform, "✅ Found", config["url"]
        elif response.status_code == 404:
            return platform, "❌ Not Found", config["url"]
        else:
            return platform, f"⚠️ Status: {response.status_code}", config["url"]
    except Exception as e:
        return platform, f"❌ Error", "-"


@invoker.entry_point
def run(
    username: sierra.Param[
        str | None,
        sierra.SierraOption(
            description="Username to check across platforms",
            mandatory="MANDATORY"
        )
    ],
    platforms: sierra.Param[
        str | None,
        sierra.SierraOption(
            description="Comma-separated platforms to check (default all)",
            mandatory="OPTIONAL"
        )
    ] = None
) -> None:
    """
    Username availability checker.
    
    Checks username across social media platforms:
    - GitHub
    - Twitter/X
    - Instagram
    - Reddit
    - LinkedIn
    - YouTube
    - Medium
    - Pinterest
    - Tumblr
    - Twitch
    
    Use --platforms to specify specific platforms (comma-separated).
    """
    if username is None:
        result = sierra.create_error_result("Missing mandatory parameter: username")
        sierra.respond(result)
        return
    
    # Determine platforms to check
    all_platforms = [
        "github", "twitter", "instagram", "reddit", "linkedin",
        "youtube", "medium", "pinterest", "tumblr", "twitch"
    ]
    
    if platforms:
        check_platforms = [p.strip().lower() for p in platforms.split(",")]
    else:
        check_platforms = all_platforms
    
    
    # Check platforms concurrently
    rows: list[list[str]] = []
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(check_platform, platform, username): platform
            for platform in check_platforms
        }
        
        for future in as_completed(futures):
            platform, status, url = future.result()
            rows.append([platform.capitalize(), status, url])
    
    # Sort by platform name
    rows.sort(key=lambda x: x[0])
    
    if rows:
        result = sierra.Table(
            headers=["Platform", "Status", "URL"],
            rows=rows
        )
    else:
        result = sierra.create_error_result("No platforms checked")
    
    sierra.respond(result)
    
    # Summary
    found_count = sum(1 for row in rows if "Found" in row[1])


def load(client: sierra.SierraDevelopmentClient) -> None:
    """Register invoker with Sierra."""
    client.load_invoker(invoker)
