# OSINT Tools Collection

Sierra SDK v2.0 includes a comprehensive collection of **15+ production-ready OSINT tools**. These tools demonstrate the power of the Sierra SDK framework and provide immediate value for investigators.

## 🚀 Available Tools

### Domain & DNS Intelligence

#### 1. `subdomain_enumerator`
**Advanced subdomain discovery using multiple techniques.**
- **Features:** Certificate Transparency logs (crt.sh), HackerTarget API, DNS bruteforce.
- **Usage:** `python example/subdomain_enumerator.py --domain example.com`

#### 2. `dns_analyzer`
**Comprehensive DNS record enumeration.**
- **Features:** A, AAAA, MX, NS, TXT, SOA, CNAME records, Reverse DNS.
- **Usage:** `python example/dns_analyzer.py --domain example.com`

#### 3. `whois_lookup`
**WHOIS information for domains and IPs.**
- **Features:** Registration details, IP geolocation, ASN info.
- **Usage:** `python example/whois_lookup.py --target example.com`

#### 4. `crt_sh`
**Certificate Transparency lookup.**
- **Features:** Subdomain discovery, email extraction.
- **Usage:** `python example/crt_sh.py --domain example.com`

---

### Network & IP Intelligence

#### 5. `ip_intelligence`
**Comprehensive IP address analysis.**
- **Features:** Geolocation, ASN, ISP, VPN/Proxy detection.
- **Usage:** `python example/ip_intelligence.py --ip 8.8.8.8`

#### 6. `port_scanner`
**Fast TCP port scanner with service detection.**
- **Features:** Concurrent scanning, service detection, custom ranges.
- **Usage:** `python example/port_scanner.py --target 192.168.1.1`

#### 7. `ssl_cert_analyzer`
**SSL/TLS certificate information.**
- **Features:** Validity check, expiration warning, SAN enumeration.
- **Usage:** `python example/ssl_cert_analyzer.py --hostname example.com`

#### 8. `rev_ip_lookup`
**Reverse IP lookup.**
- **Features:** Find domains hosted on the same IP.
- **Usage:** `python example/rev_ip_lookup.py --ip 192.168.1.1`

---

### Email OSINT

#### 9. `email_breach_checker`
**Check email addresses in data breaches.**
- **Features:** Have I Been Pwned integration, password hash check.
- **Usage:** `python example/email_breach_checker.py --email user@example.com`

#### 10. `whosemail`
**Email investigation.**
- **Features:** Domain verification, MX record check.
- **Usage:** `python example/whosemail.py --email user@example.com`

---

### Web & Technology OSINT

#### 11. `tech_detector`
**Detect web technologies and frameworks.**
- **Features:** CMS, frameworks, analytics, CDN detection.
- **Usage:** `python example/tech_detector.py --url https://example.com`

#### 12. `wayback_analyzer`
**Website history via Wayback Machine.**
- **Features:** Historical snapshots, archive timeline.
- **Usage:** `python example/wayback_analyzer.py --url example.com`

---

### Social Media & Identity

#### 13. `username_checker`
**Check username across 10+ platforms.**
- **Features:** GitHub, Twitter, Instagram, Reddit, etc.
- **Usage:** `python example/username_checker.py --username johndoe`

#### 14. `digital_footprint`
**Comprehensive digital footprint analysis.**
- **Features:** Aggregates data from multiple sources.
- **Usage:** `python example/digital_footprint.py --target user@example.com`

#### 15. `phone_number`
**Phone number investigation.**
- **Features:** Carrier info, location data.
- **Usage:** `python example/phone_number.py --number "+1234567890"`

---

## 🛠️ Installation

These tools are included in the `example/` directory of the Sierra SDK.

1.  **Install Dependencies:**
    ```bash
    pip install requests dnspython beautifulsoup4
    ```

2.  **Add to Environment:**
    Copy the scripts to your Sierra SDK environment's `scripts` directory or symlink them.

    ```bash
    cp example/*.py /path/to/your/sierra-env/scripts/
    ```

3.  **Build:**
    ```bash
    sierra-dev build --env your_env
    ```

## 📝 Creating Your Own Tools

You can use these tools as templates for creating your own invokers. See the [Development Guide](development.md) for more details.
