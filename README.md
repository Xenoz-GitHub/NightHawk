# ENCRYPTED CREW - NIGHTHAWK 🦅

```
  ███████╗███╗   ██╗ ██████╗██████╗ ██╗   ██╗██████╗ ████████╗███████╗██████╗ 
  ██╔════╝████╗  ██║██╔════╝██╔══██╗╚██╗ ██╔╝██╔══██╗╚══██╔══╝██╔════╝██╔══██╗
  █████╗  ██╔██╗ ██║██║     ██████╔╝ ╚████╔╝ ██████╔╝   ██║   █████╗  ██║  ██║
  ██╔══╝  ██║╚██╗██║██║     ██╔══██╗  ╚██╔╝  ██╔═══╝    ██║   ██╔══╝  ██║  ██║
  ███████╗██║ ╚████║╚██████╗██║  ██║   ██║   ██║        ██║   ███████╗██████╔╝
  ╚══════╝╚═╝  ╚═══╝ ╚═════╝╚═╝  ╚═╝   ╚═╝   ╚═╝        ╚═╝   ╚══════╝╚═════╝ 
                                                                                
   ██████╗██████╗ ███████╗██╗    ██╗                                          
  ██╔════╝██╔══██╗██╔════╝██║    ██║                                          
  ██║     ██████╔╝█████╗  ██║ █╗ ██║                                          
  ██║     ██╔══██╗██╔══╝  ██║███╗██║                                          
  ╚██████╗██║  ██║███████╗╚███╔███╔╝                                          
   ╚═════╝╚═╝  ╚═╝╚══════╝ ╚══╝╚══╝                                           

  ════════════════════════════════════════════════════════════════════════════
  🦅 NIGHTHAWK v2.0.0 | Ethical Red-Team Reconnaissance Platform
  ⚡ Attack Surface Discovery • Security Assessment • Threat Intelligence
  ════════════════════════════════════════════════════════════════════════════
```

**Professional Ethical Red-Team Reconnaissance & Attack-Surface Assessment Platform**

> ⚠️ **STRICTLY INTENDED FOR AUTHORIZED USE ONLY**  
> For systems owned by the user, isolated cybersecurity labs, CTF environments, explicitly authorized penetration tests, and security research environments.

---

## 🌟 Features

### Core Capabilities
- 🌐 **Web Security Assessment** - TLS/SSL analysis, security headers, cookie inspection, redirect chain analysis
- 🔍 **Network Discovery** - Port scanning, service fingerprinting, banner grabbing
- 🛠️ **Technology Detection** - Framework & CMS identification with confidence scoring
- 🔐 **Secret Scanning** - Detect exposed API keys, credentials, tokens in source code
- 📊 **Comprehensive Reporting** - HTML, JSON, CSV export with professional formatting
- 🎯 **Scope Management** - Mandatory authorization enforcement before any assessment

### Enhanced in v2.0.0
- ✨ **Professional UI/UX** - Cyberpunk-inspired green/cyan/red ethical hacker theme
- 🎨 **ENCRYPTED CREW Branding** - Custom ASCII art banners and styled output
- 🔧 **Improved Error Handling** - Better messages, graceful failures, helpful suggestions
- 🌍 **Global Compatibility** - Enhanced Windows/Linux/macOS support
- 📝 **Optional Scope Mode** - Can bypass scope validation with `--skip-scope` flag
- 💾 **Export Options** - Save results to JSON for further analysis
- ⚡ **Interactive Features** - Progress indicators, status updates, colored output
- 🐛 **Bug Fixes** - Fixed `--version` flag, scope.yaml requirements, and edge cases

---

## 🚀 Quick Start

### Installation

```bash
# Install from source (recommended for latest features)
git clone https://github.com/Xenoz-GitHub/NightHawk.git
cd NightHawk
pip install -e .

# Or install directly from GitHub
pip install git+https://github.com/Xenoz-GitHub/NightHawk.git

# Or use pipx (isolated environment)
pipx install git+https://github.com/Xenoz-GitHub/NightHawk.git
```

### Verify Installation

```bash
nighthawk --version
```

### First Steps

1. **Create Scope Configuration** (Required for ethical assessments)
```bash
nighthawk scope --create
```

2. **Edit `scope.yaml`** to add your authorized targets
```yaml
domains:
  - example.com
  - test.example.com

ips:
  - 192.168.1.1

modules:
  - web
  - network
  - secrets
  - technology
```

3. **Run Assessments**
```bash
# Web security assessment
nighthawk web https://example.com

# Network discovery
nighthawk discover 192.168.1.1

# Technology fingerprinting
nighthawk tech https://example.com

# Secret scanning
nighthawk secrets /path/to/repo

# Full assessment campaign
nighthawk assess
```

---

## 📖 Command Reference

### Display Banner & Version
```bash
nighthawk --version          # Show version with banner
nighthawk --banner           # Display full ASCII banner
nighthawk --help             # Show help menu
```

### Scope Management
```bash
nighthawk scope --create                    # Create example scope.yaml
nighthawk scope --file custom-scope.yaml    # Validate custom scope
```

### Web Assessment
```bash
nighthawk web <url> [OPTIONS]

Options:
  --scope, -s TEXT           Scope file (default: scope.yaml)
  --skip-scope              Skip scope validation
  --timeout, -t INTEGER     Request timeout in seconds
  --export, -e TEXT         Export results to JSON file
  --follow-redirects        Follow HTTP redirects (default: on)

Examples:
  nighthawk web https://example.com
  nighthawk web https://api.example.com --export results.json
  nighthawk web https://test.com --skip-scope --timeout 60
```

### Network Discovery
```bash
nighthawk discover <target> [OPTIONS]

Options:
  --scope, -s TEXT         Scope file (default: scope.yaml)
  --skip-scope            Skip scope validation
  --ports, -p TEXT        Port range (default: 1-1000)
  --timeout, -t INTEGER   Connection timeout

Examples:
  nighthawk discover 192.168.1.1
  nighthawk discover 10.0.0.0/24 --ports 1-65535
  nighthawk discover example.com --skip-scope
```

### Technology Detection
```bash
nighthawk tech <url> [OPTIONS]

Options:
  --scope, -s TEXT       Scope file
  --skip-scope          Skip scope validation
  --export, -e TEXT     Export to JSON

Examples:
  nighthawk tech https://example.com
  nighthawk tech https://wordpress-site.com --export tech.json
```

### Secret Scanning
```bash
nighthawk secrets <path> [OPTIONS]

Options:
  --scope, -s TEXT          Scope file
  --skip-scope             Skip scope validation
  --export, -e TEXT        Export to JSON
  --redact/--no-redact     Redact sensitive values (default: on)

Examples:
  nighthawk secrets /path/to/repo
  nighthawk secrets . --export secrets.json
  nighthawk secrets ~/projects --no-redact --skip-scope
```

### Full Assessment Campaign
```bash
nighthawk assess [OPTIONS]

Options:
  --scope, -s TEXT        Scope file (default: scope.yaml)
  --modules, -m TEXT      Comma-separated modules (default: all)

Examples:
  nighthawk assess
  nighthawk assess --modules web,network,tech
  nighthawk assess --scope production-scope.yaml
```

### Report Generation
```bash
nighthawk report <campaign-id> [OPTIONS]

Options:
  --output, -o TEXT     Output file path (default: report.html)
  --format, -f TEXT     Format: html, json, csv (default: html)

Examples:
  nighthawk report latest
  nighthawk report abc-123-def --format json
  nighthawk report xyz-789 --output custom-report.html
```

---

## 🎨 Theme & Styling

ENCRYPTED CREW NIGHTHAWK features a professional ethical hacker theme:

- **🟢 Green** - Success messages, valid configurations, secure findings
- **🔵 Cyan** - Information, headers, primary interface elements  
- **🔴 Red** - Errors, vulnerabilities, critical findings
- **🟡 Yellow** - Warnings, medium-risk items, suggestions
- **⚪ White** - Standard text, descriptions

### Visual Elements
- ✓ Success indicators
- ✗ Error indicators
- ⚠ Warning indicators
- ℹ Information indicators
- 🦅 NIGHTHAWK bird icon
- ⚡ Lightning bolt for features
- 🔒 Lock for security elements

---

## 🏗️ Architecture

### Technology Stack
- **Core**: Python 3.11+
- **CLI Framework**: Typer with Rich formatting
- **API**: FastAPI (REST endpoints)
- **Database**: SQLAlchemy + Alembic migrations
- **Frontend**: React + TypeScript (dashboard)
- **Async**: asyncio, httpx for concurrent operations

### Key Modules
```
src/nighthawk/
├── cli/            # Command-line interface
│   ├── main.py     # Command definitions
│   └── banner.py   # ENCRYPTED CREW branding
├── scope/          # Authorization & target management
├── web/            # Web security scanner
├── network/        # Network discovery
├── technology/     # Fingerprinting engine
├── secrets/        # Secret detection
├── reporting/      # Report generation
├── correlation/    # Finding relationships
└── orchestrator/   # Campaign management
```

---

## 🔒 Security & Ethics

### Security Boundaries
- ❌ No malware, ransomware, or destructive actions
- ❌ No credential theft or persistence mechanisms
- ❌ No unauthorized exploitation or covert surveillance
- ✅ Mandatory scope validation before execution
- ✅ Default redaction for secrets in logs
- ✅ Least-privilege design with safe defaults

### Ethical Usage Guidelines
1. **Always obtain explicit written authorization** before scanning
2. **Stay within defined scope** - use scope.yaml for all assessments
3. **Respect rate limits** and system resources
4. **Document all activities** for audit trails
5. **Report vulnerabilities responsibly** to affected parties
6. **Comply with local laws** and regulations (CFAA, GDPR, etc.)

### Legal Notice
Unauthorized access to computer systems is illegal. This tool is for authorized security testing only. Users are solely responsible for ensuring proper authorization and compliance with applicable laws.

---

## 🛠️ Development

### Setup Development Environment
```bash
# Clone repository
git clone https://github.com/Xenoz-GitHub/NightHawk.git
cd NightHawk

# Install with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Code Quality
```bash
# Run linter
make lint

# Format code
make format

# Run tests
make test

# Build package
make build
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/nighthawk --cov-report=html

# Run specific test module
pytest tests/test_web.py -v
```

---

## 📦 Project Structure

```
ENCRYPTED-CREW-CHECKING-TOOL/
├── src/nighthawk/          # Source code
│   ├── cli/               # CLI commands & branding
│   ├── web/               # Web scanner
│   ├── network/           # Network scanner
│   ├── technology/        # Tech detection
│   ├── secrets/           # Secret scanner
│   ├── scope/             # Authorization
│   ├── reporting/         # Report generation
│   └── ...
├── tests/                 # Test suite
├── docs/                  # Documentation
├── templates/             # Report templates
├── fingerprints/          # Technology signatures
├── rules/                 # Detection rules
├── scope.yaml             # Target authorization
├── pyproject.toml         # Project configuration
└── README.md              # This file
```

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Contribution Guidelines
- Follow PEP 8 style guide
- Add tests for new features
- Update documentation
- Ensure all tests pass
- Maintain security boundaries

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details

---

## 🙏 Acknowledgments

- Original NightHawk project by Xenoz-GitHub
- ENCRYPTED CREW for enhanced features and branding
- Security research community for best practices
- Open-source contributors and maintainers

---

## 📞 Support & Contact

- **Issues**: [GitHub Issues](https://github.com/Xenoz-GitHub/NightHawk/issues)
- **Documentation**: [GitHub Wiki](https://github.com/Xenoz-GitHub/NightHawk/wiki)
- **Security**: Report vulnerabilities via GitHub Security Advisories

---

## 🚨 Disclaimer

This tool is provided "as is" without warranty of any kind. Use at your own risk. The authors and contributors are not responsible for any misuse or damage caused by this tool. Always obtain proper authorization before conducting security assessments.

---

<div align="center">

**ENCRYPTED CREW - NIGHTHAWK v2.0.0**

*Professional Ethical Red-Team Reconnaissance Platform*

Made with ❤️ by security researchers, for security researchers

</div>
