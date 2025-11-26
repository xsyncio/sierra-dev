"""
Web Technology Detection Tool.

Identify technologies, frameworks, and services used by websites.
"""
import typing
import requests
import re
from urllib.parse import urlparse

import sierra

invoker = sierra.InvokerScript(
    name="tech_detector",
    description="Detect web technologies frameworks and services"
)

invoker.requirement(["requests", "beautifulsoup4"])


@invoker.dependancy
def fetch_website(url: str) -> tuple[str, dict[str, str]]:
    """Fetch website content and headers."""
    try:
        if not url.startswith(('http://', 'https://')):
            url = f"https://{url}"
        
        response = requests.get(url, timeout=15, allow_redirects=True)
        return response.text, dict(response.headers)
    except Exception as e:
        return "", {}


@invoker.dependancy
def detect_technologies(html: str, headers: dict[str, str]) -> dict[str, list[str]]:
    """Detect technologies from HTML and headers."""
    detected: dict[str, list[str]] = {
        "cms": [],
        "frameworks": [],
        "analytics": [],
        "cdn": [],
        "servers": [],
        "languages": [],
        "other": []
    }
    
    html_lower = html.lower()
    
    # CMS Detection
    if "wp-content" in html_lower or "wordpress" in html_lower:
        detected["cms"].append("WordPress")
    if "joomla" in html_lower:
        detected["cms"].append("Joomla")
    if "drupal" in html_lower:
        detected["cms"].append("Drupal")
    if "shopify" in html_lower or "cdn.shopify.com" in html_lower:
        detected["cms"].append("Shopify")
    if "wix" in html_lower:
        detected["cms"].append("Wix")
    
    # Frameworks
    if "react" in html_lower or "_reactroot" in html_lower:
        detected["frameworks"].append("React")
    if "angular" in html_lower or "ng-" in html:
        detected["frameworks"].append("Angular")
    if "vue" in html_lower:
        detected["frameworks"].append("Vue.js")
    if "next" in html_lower or "_next" in html:
        detected["frameworks"].append("Next.js")
    if "bootstrap" in html_lower:
        detected["frameworks"].append("Bootstrap")
    if "tailwind" in html_lower:
        detected["frameworks"].append("Tailwind CSS")
    
    # Analytics
    if "google-analytics" in html_lower or "gtag" in html_lower:
        detected["analytics"].append("Google Analytics")
    if "facebook" in html_lower and "pixel" in html_lower:
        detected["analytics"].append("Facebook Pixel")
    if "hotjar" in html_lower:
        detected["analytics"].append("Hotjar")
    if "mixpanel" in html_lower:
        detected["analytics"].append("Mixpanel")
    
    # CDN
    if "cloudflare" in html_lower or "cf-ray" in str(headers).lower():
        detected["cdn"].append("Cloudflare")
    if "akamai" in html_lower:
        detected["cdn"].append("Akamai")
    if "fastly" in html_lower:
        detected["cdn"].append("Fastly")
    if "cloudfront" in html_lower:
        detected["cdn"].append("Amazon CloudFront")
    
    # Server from headers
    server_header = headers.get("Server", headers.get("server", ""))
    if server_header:
        detected["servers"].append(server_header)
    
    # Language hints
    if ".php" in html_lower or "php" in server_header.lower():
        detected["languages"].append("PHP")
    if ".asp" in html_lower or "asp.net" in html_lower:
        detected["languages"].append("ASP.NET")
    if "django" in html_lower:
        detected["languages"].append("Python/Django")
    if "rails" in html_lower or "ruby" in html_lower:
        detected["languages"].append("Ruby on Rails")
    
    # Other
    if "jquery" in html_lower:
        detected["other"].append("jQuery")
    if "stripe" in html_lower:
        detected["other"].append("Stripe (Payments)")
    if "recaptcha" in html_lower:
        detected["other"].append("Google reCAPTCHA")
    
    return detected


@invoker.entry_point
def run(
    url: sierra.Param[
        str | None,
        sierra.SierraOption(
            description="Website URL to analyze",
            mandatory="MANDATORY"
        )
    ]
) -> None:
    """
    Technology detection tool.
    
    Identifies technologies used by a website:
    - CMS (WordPress, Joomla, Drupal, etc.)
    - Frameworks (React, Angular, Vue, etc.)
    - Analytics (Google Analytics, Facebook Pixel, etc.)
    - CDN (Cloudflare, Akamai, etc.)
    - Server software
    - Programming languages
    """
    if url is None:
        result = sierra.create_error_result("Missing mandatory parameter: url")
        sierra.respond(result)
        return
    
    
    # Fetch website
    html, headers = fetch_website(url)
    
    if not html and not headers:
        result = sierra.create_error_result(f"Failed to fetch website: {url}")
        sierra.respond(result)
        return
    
    # Detect technologies
    techs = detect_technologies(html, headers)
    
    # Build result table
    rows: list[list[str]] = []
    
    for category, items in techs.items():
        if items:
            category_name = category.upper().replace("_", " ")
            rows.append([category_name, ", ".join(items)])
    
    if rows:
        result = sierra.Table(
            headers=["Category", "Technologies"],
            rows=rows
        )
    else:
        result = sierra.create_error_result("No technologies detected")
    
    sierra.respond(result)


def load(client: sierra.SierraDevelopmentClient) -> None:
    """Register invoker with Sierra."""
    client.load_invoker(invoker)
