# ENCRYPTED CREW - NIGHTHAWK Quick Start Guide

This guide will get you up and running with NIGHTHAWK in under 5 minutes.

##  Installation

### Option 1: Install from Source (Recommended)
```bash
# Clone the repository
git clone https://github.com/Xenoz-GitHub/NightHawk.git
cd NightHawk

# Install in development mode
pip install -e .

# Verify installation
nighthawk --version
```

### Option 2: Direct Install from GitHub
```bash
pip install git+https://github.com/Xenoz-GitHub/NightHawk.git
nighthawk --version
```

### Option 3: Using pipx (Isolated Environment)
```bash
pipx install git+https://github.com/Xenoz-GitHub/NightHawk.git
nighthawk --version
```

##  Verify Installation

You should see the ENCRYPTED CREW banner and version information:
```
nighthawk --version
```

##  First Steps

### Step 1: Create Scope Configuration

Before performing any assessments, create an authorization scope:

```bash
nighthawk scope --create
```

This creates a `scope.yaml` file in your current directory.

### Step 2: Edit Scope File

Open `scope.yaml` and add your authorized targets:

```yaml
# Example scope.yaml
domains:
  - example.com
  - test.example.com

ips:
  - 192.168.1.1
  - 10.0.0.1

cidrs:
  - 192.168.1.0/24

modules:
  - web
  - network
  - secrets
  - technology
```

### Step 3: Validate Scope

```bash
nighthawk scope
```

You should see a confirmation that your scope is valid.

##  Basic Usage Examples

### Web Security Assessment
```bash
# Basic web scan
nighthawk web https://example.com

# Web scan with export
nighthawk web https://example.com --export results.json

# Skip scope validation (use with caution!)
nighthawk web https://example.com --skip-scope
```

### Network Discovery
```bash
# Scan a single host
nighthawk discover 192.168.1.1

# Scan specific ports
nighthawk discover 192.168.1.1 --ports 1-1000

# Scan a CIDR range
nighthawk discover 192.168.1.0/24
```

### Technology Detection
```bash
# Detect web technologies
nighthawk tech https://example.com

# Export results
nighthawk tech https://example.com --export tech.json
```

### Secret Scanning
```bash
# Scan current directory
nighthawk secrets .

# Scan specific path
nighthawk secrets /path/to/repository

# Export findings
nighthawk secrets /path/to/repo --export secrets.json
```

### Full Assessment Campaign
```bash
# Run all modules on all scope targets
nighthawk assess

# Run specific modules
nighthawk assess --modules web,network
```

##  Configuration

### View Current Configuration
```bash
nighthawk config show
```

### Customize Settings
```bash
# Change theme color
nighthawk config set --key theme.primary_color --value green

# Disable banner
nighthawk config set --key theme.show_banner --value false

# Set default timeout
nighthawk config set --key scan.default_timeout --value 60
```

### Export Example Config
```bash
nighthawk config export --output my-config.json
# Edit my-config.json and place in ~/.nighthawk/config.json
```

### Reset to Defaults
```bash
nighthawk config reset
```

##  Common Workflows

### Workflow 1: Quick Web Assessment
```bash
# Create scope
nighthawk scope --create
# Edit scope.yaml with your target

# Run web assessment
nighthawk web https://your-target.com --export web-results.json

# Check technologies
nighthawk tech https://your-target.com --export tech-results.json
```

### Workflow 2: Network Reconnaissance
```bash
# Create scope with IP ranges
nighthawk scope --create
# Edit scope.yaml

# Discover network assets
nighthawk discover 192.168.1.0/24 --ports 1-1000

# Full assessment
nighthawk assess --modules network,web
```

### Workflow 3: Code Security Review
```bash
# Create scope with repository path
nighthawk scope --create
# Edit scope.yaml

# Scan for secrets
nighthawk secrets /path/to/code --export secrets-report.json

# Review findings in the exported JSON
```

##  Security Best Practices

1. **Always Get Authorization**: Never scan systems you don't own or have explicit permission to test
2. **Use Scope Files**: Define authorized targets in `scope.yaml` before scanning
3. **Redact Secrets**: Keep default redaction enabled when sharing results
4. **Rate Limiting**: Be respectful of target systems - use appropriate timeouts
5. **Document Everything**: Keep records of authorization and findings

##  Troubleshooting

### Issue: "Scope file not found"
**Solution**: Create a scope file with `nighthawk scope --create` or use `--skip-scope` flag (not recommended)

### Issue: "--version flag shows error"
**Solution**: Update to v2.0.0+ or use `nighthawk --help` to verify installation

### Issue: "Permission denied" errors
**Solution**:
- On Windows: Run as Administrator for network scans
- On Linux/Mac: Use `sudo` for privileged port scans (< 1024)

### Issue: Import errors
**Solution**: Reinstall dependencies:
```bash
pip install -e . --force-reinstall
```

### Issue: Config not loading
**Solution**: Check config location:
```bash
# Config should be at:
# Windows: C:\Users\YourName\.nighthawk\config.json
# Linux/Mac: ~/.nighthawk/config.json
```

##  Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [docs/](docs/) for architecture and plugin development
- Review example scope files in [examples/](examples/)
- Join the community and report issues on GitHub

##  Getting Help

```bash
# General help
nighthawk --help

# Command-specific help
nighthawk web --help
nighthawk discover --help
nighthawk scope --help

# Show banner and version
nighthawk --version
```

##  Quick Reference

| Command | Purpose |
|---------|---------|
| `nighthawk --version` | Show version with banner |
| `nighthawk scope --create` | Create scope file |
| `nighthawk web <url>` | Web security scan |
| `nighthawk discover <target>` | Network discovery |
| `nighthawk tech <url>` | Technology detection |
| `nighthawk secrets <path>` | Secret scanning |
| `nighthawk assess` | Full campaign |
| `nighthawk config show` | View configuration |
| `nighthawk report <id>` | Generate report |

---

<div align="center">

**ENCRYPTED CREW - NIGHTHAWK v2.0.0**

*Professional Ethical Red-Team Reconnaissance Platform*

 Ready to start? Run: `nighthawk --version`

</div>
