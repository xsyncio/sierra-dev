# Sierra OSINT Toolkit - Example Tools

A comprehensive collection of production-ready OSINT (Open Source Intelligence) tools built with the Sierra framework.

## 🚀 Available Tools (15+)

### Domain & DNS Intelligence

#### 1. subdomain_enumerator.py
**Advanced subdomain discovery using multiple techniques**
- Certificate Transparency logs (crt.sh)
- HackerTarget API integration
- Optional DNS bruteforce
- Concurrent scanning for speed

```bash
sierra run subdomain-enumerator --domain example.com
sierra run subdomain-enumerator --domain example.com --wordlist true
```

#### 2. dns_analyzer.py
**Comprehensive DNS record enumeration**
- A, AAAA, MX, NS, TXT, SOA, CNAME records
- Reverse DNS lookup
- Customizable record types

```bash
sierra run dns-analyzer --domain example.com
sierra run dns-analyzer --domain example.com --record-types "A,MX,TXT"
```

#### 3. whois_lookup.py
**WHOIS information for domains and IPs**
- Domain registration details
- IP geolocation
- ASN and organization info
- Nameserver information

```bash
sierra run whois-lookup --target example.com
sierra run whois-lookup --target 8.8.8.8
```

#### 4. crt_sh.py *(Original)*
**Certificate Transparency lookup**
- Subdomain discovery
- Email address extraction
- Tree-based result display

```bash
sierra run crtsh-extended --domain example.com
```

---

### Network & IP Intelligence

#### 5. ip_intelligence.py
**Comprehensive IP address analysis**
- Geolocation (city, region, country)
- Network information (ASN, ISP)
- VPN/Proxy detection
- Reverse DNS lookup
- Timezone and coordinates

```bash
sierra run ip-intelligence --ip 8.8.8.8
```

#### 6. port_scanner.py
**Fast TCP port scanner with service detection**
- Concurrent scanning
- Common ports preset
- Port ranges and custom lists
- Service name detection

```bash
sierra run port-scanner --target 192.168.1.1 --ports common
sierra run port-scanner --target example.com --ports "80,443,8080" --threads 100
sierra run port-scanner --target 192.168.1.1 --ports "1-1000"
```

#### 7. ssl_cert_analyzer.py
**SSL/TLS certificate information**
- Subject and issuer details
- Validity and expiration warnings
- SAN (Subject Alternative Names)
- Technical details

```bash
sierra run ssl-cert-analyzer --hostname example.com
sierra run ssl-cert-analyzer --hostname example.com --port 8443
```

#### 8. rev_ip_lookup.py *(Original)*
**Reverse IP lookup**
- Find domains hosted on same IP

```bash
sierra run rev-ip-lookup --ip 192.168.1.1
```

---

### Email OSINT

#### 9. email_breach_checker.py
**Check email addresses in data breaches**
- Have I Been Pwned API integration
- Password hash checking
- Detailed breach information

```bash
sierra run email-breach-checker --email user@example.com
sierra run email-breach-checker --email user@example.com --check-password "password123"
```

**Note**: Requires HIBP API key from https://haveibeenpwned.com/API/Key

#### 10. whosemail.py *(Original)*
**Email investigation**

```bash
sierra run whosemail --email user@example.com
```

---

### Web & Technology OSINT

#### 11. tech_detector.py
**Detect web technologies and frameworks**
- CMS detection (WordPress, Joomla, Drupal, Shopify, etc.)
- Frameworks (React, Angular, Vue, Next.js, etc.)
- Analytics (Google Analytics, Facebook Pixel, etc.)
- CDN (Cloudflare, Akamai, etc.)
- Server and language detection

```bash
sierra run tech-detector --url https://example.com
```

#### 12. wayback_analyzer.py
**Website history via Wayback Machine**
- Historical snapshots
- First/last archive dates
- Direct links to archived versions

```bash
sierra run wayback-analyzer --url example.com
sierra run wayback-analyzer --url example.com --limit 20
```

---

### Social Media & Identity

#### 13. username_checker.py
**Check username across 10+ platforms**
- GitHub, Twitter/X, Instagram
- Reddit, LinkedIn, YouTube
- Medium, Pinterest, Tumblr, Twitch
- Concurrent checking for speed

```bash
sierra run username-checker --username johndoe
sierra run username-checker --username johndoe --platforms "github,twitter,linkedin"
```

#### 14. digital_footprint.py *(Original)*
**Comprehensive digital footprint analysis**

```bash
sierra run digital-footprint --target user@example.com
```

#### 15. phone_number.py *(Original)*
**Phone number investigation**

```bash
sierra run phone-number --number "+1234567890"
```

---

## 🎯 Features

All tools include:
- ✅ **Type-safe** - Full type annotations
- ✅ **Error handling** - Graceful failure handling
- ✅ **Rich output** - Tables, trees, and structured results
- ✅ **Documentation** - Comprehensive docstrings
- ✅ **Production-ready** - Real API integration
- ✅ **Concurrent** - Fast execution where applicable

---

## 📦 Installation

### 1. Install Sierra Dev
```bash
cd /path/to/sierra-dev
pip install -e .
```

### 2. Install Tool Dependencies
```bash
# For all tools
pip install requests dnspython beautifulsoup4

# Individual tool requirements
# - subdomain_enumerator: requests, dnspython
# - dns_analyzer: dnspython
# - whois_lookup: requests
# - email_breach_checker: requests
# - tech_detector: requests, beautifulsoup4
# - All others: requests
```

### 3. Add Examples to Sierra Environment
```bash
# Create symlinks or copy to your Sierra environment scripts folder
cp example/*.py /path/to/your/sierra-env/scripts/
```

---

## 🔧 Usage

### Build Environment
```bash
sierra build --env your_env
```

### Run Tools
```bash
# List available tools
sierra list --installed

# Run a tool
sierra run <tool-name> --param value

# Get help
sierra run <tool-name> --help
```

---

## 🌟 Use Cases

### Security Auditing
- `port_scanner` - Find open ports
- `ssl_cert_analyzer` - Check certificate validity
- `tech_detector` - Identify vulnerable technologies

### Penetration Testing
- `subdomain_enumerator` - Expand attack surface
- `dns_analyzer` - DNS reconnaissance
- `wayback_analyzer` - Find old vulnerabilities

### Threat Intelligence
- `email_breach_checker` - Check for compromised credentials
- `ip_intelligence` - Geolocate threats
- `username_checker` - Track online presence

### Due Diligence
- `whois_lookup` - Domain ownership research
- `digital_footprint` - Person/email investigation
- `tech_detector` - Technology stack analysis

---

## 🛡️ API Keys & Rate Limits

Some tools require API keys:

- **email_breach_checker** - HIBP API key
  - Get from: https://haveibeenpwned.com/API/Key
  - Edit file and replace `YOUR_API_KEY_HERE`

- **Rate Limits**:
  - Most public APIs have rate limits
  - Use responsibly
  - Implement delays if needed

---

## 🎓 Creating Your Own Tools

Use these examples as templates! Key patterns:

```python
import sierra

# Create invoker
invoker = sierra.InvokerScript(
    name="my-tool",
    description="My OSINT tool"
)

# Declare dependencies
invoker.requirement(["requests"])

# Helper functions
@invoker.dependancy
def helper_function(param: str) -> dict:
    # implementation
    return {}

# Entry point
@invoker.entry_point
def run(
    target: sierra.Param[
        str | None,
        sierra.SierraOption(
            description="Target to analyze",
            mandatory="MANDATORY"
        )
    ]
) -> None:
    # Tool logic
    result = sierra.Table(headers=["Col1"], rows=[["Data"]])
    print(result)

# Load hook
def load(client: sierra.SierraDevelopmentClient) -> None:
    client.load_invoker(invoker)
```

---

## 📊 Result Types

All tools use rich result types:

```python
# Tables
sierra.Table(headers=["IP", "Status"], rows=[["8.8.8.8", "Active"]])

# Trees
sierra.create_tree_result(["Root", {"Branch": ["Leaf"]}])

# Errors
sierra.create_error_result("Error message")
```

---

## 🤝 Contributing

Feel free to:
- Add new OSINT tools
- Improve existing tools
- Fix bugs
- Add features

Follow the existing code style and ensure:
- Type annotations on all functions
- Proper error handling
- Clear documentation
- Real-world testing

---

## ⚠️ Legal & Ethical Use

These tools are for:
- ✅ Security research with permission
- ✅ Bug bounty programs
- ✅ Authorized penetration testing
- ✅ Educational purposes

NOT for:
- ❌ Unauthorized access
- ❌ Illegal activities
- ❌ Privacy violations
- ❌ Harassment or stalking

**Always obtain proper authorization before testing systems you don't own.**

---

## 📝 License

These examples are provided as-is for educational and research purposes.

---

**Built with ❤️ using the Sierra Dev**
