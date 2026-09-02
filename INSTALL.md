# ENCRYPTED CREW - NIGHTHAWK Installation Guide

Complete installation instructions for Windows, Linux, and macOS.

## 📋 Prerequisites

### System Requirements
- **Operating System**: Windows 10/11, Linux (Ubuntu 20.04+, Debian, etc.), macOS 10.15+
- **Python**: 3.11 or higher
- **Memory**: 2GB RAM minimum, 4GB recommended
- **Disk Space**: 500MB for installation and dependencies
- **Network**: Internet connection for package downloads

### Required Software
- Python 3.11+ with pip
- Git (for cloning repository)
- C compiler (for some dependencies on Linux/macOS)

---

## 🪟 Windows Installation

### Method 1: Install from Source (Recommended)

1. **Install Python 3.11+**
   ```powershell
   # Download from python.org or use winget
   winget install Python.Python.3.11
   ```

2. **Install Git**
   ```powershell
   winget install Git.Git
   ```

3. **Clone Repository**
   ```powershell
   cd D:\TOOLS
   git clone https://github.com/Xenoz-GitHub/NightHawk.git ENCRYPTED-CREW-CHECKING-TOOL
   cd ENCRYPTED-CREW-CHECKING-TOOL
   ```

4. **Install Package**
   ```powershell
   pip install -e .
   ```

5. **Verify Installation**
   ```powershell
   nighthawk --version
   ```

### Method 2: Direct Install from GitHub

```powershell
pip install git+https://github.com/Xenoz-GitHub/NightHawk.git
nighthawk --version
```

### Method 3: Using pipx (Isolated Environment)

```powershell
# Install pipx
pip install pipx
pipx ensurepath

# Install nighthawk
pipx install git+https://github.com/Xenoz-GitHub/NightHawk.git

# Verify
nighthawk --version
```

### Windows Troubleshooting

**Issue: "pip is not recognized"**
```powershell
# Add Python to PATH or use full path
C:\Users\YourName\AppData\Local\Programs\Python\Python311\Scripts\pip.exe install -e .
```

**Issue: "Permission denied"**
```powershell
# Run PowerShell as Administrator or use --user flag
pip install --user -e .
```

**Issue: "Execution policy error"**
```powershell
# Set execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Issue: "Console encoding errors"**
- The tool automatically handles this in v2.0.0
- Uses fallback ASCII characters when Unicode isn't supported

---

## 🐧 Linux Installation

### Ubuntu/Debian

1. **Install Prerequisites**
   ```bash
   sudo apt update
   sudo apt install python3.11 python3-pip python3-venv git build-essential
   ```

2. **Clone Repository**
   ```bash
   cd /opt
   sudo git clone https://github.com/Xenoz-GitHub/NightHawk.git encrypted-crew-nighthawk
   cd encrypted-crew-nighthawk
   ```

3. **Create Virtual Environment (Optional but Recommended)**
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate
   ```

4. **Install Package**
   ```bash
   pip install -e .
   ```

5. **Verify Installation**
   ```bash
   nighthawk --version
   ```

### Fedora/RHEL/CentOS

```bash
# Install prerequisites
sudo dnf install python3.11 python3-pip git gcc

# Clone and install
git clone https://github.com/Xenoz-GitHub/NightHawk.git
cd NightHawk
pip install -e .
```

### Arch Linux

```bash
# Install prerequisites
sudo pacman -S python python-pip git base-devel

# Clone and install
git clone https://github.com/Xenoz-GitHub/NightHawk.git
cd NightHawk
pip install -e .
```

### Linux Troubleshooting

**Issue: "Permission denied on privileged ports"**
```bash
# Use sudo for ports < 1024
sudo nighthawk discover 192.168.1.1 --ports 1-1000

# Or use capability (preferred)
sudo setcap cap_net_raw,cap_net_admin=eip $(which python3)
```

**Issue: "ModuleNotFoundError"**
```bash
# Reinstall with verbose output
pip install -e . -v
```

---

## 🍎 macOS Installation

### Using Homebrew

1. **Install Homebrew** (if not already installed)
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Install Python**
   ```bash
   brew install python@3.11 git
   ```

3. **Clone Repository**
   ```bash
   cd ~/Projects
   git clone https://github.com/Xenoz-GitHub/NightHawk.git
   cd NightHawk
   ```

4. **Install Package**
   ```bash
   pip3 install -e .
   ```

5. **Verify Installation**
   ```bash
   nighthawk --version
   ```

### Using Python.org Installer

1. Download Python 3.11+ from python.org
2. Install Python
3. Follow Linux instructions above

### macOS Troubleshooting

**Issue: "xcrun: error: invalid active developer path"**
```bash
# Install Xcode Command Line Tools
xcode-select --install
```

**Issue: "SSL certificate errors"**
```bash
# Install certificates
/Applications/Python\ 3.11/Install\ Certificates.command
```

---

## 🔧 Post-Installation Setup

### 1. Verify Installation
```bash
nighthawk --version
nighthawk --help
```

You should see the ENCRYPTED CREW banner and version 2.0.0.

### 2. Create Configuration Directory
```bash
# Windows
mkdir %USERPROFILE%\.nighthawk

# Linux/macOS
mkdir ~/.nighthawk
```

### 3. Create Scope File
```bash
nighthawk scope --create
```

Edit `scope.yaml` with your authorized targets.

### 4. Export Configuration Template
```bash
nighthawk config export --output ~/.nighthawk/config.json
```

Edit `config.json` to customize settings.

### 5. Test Commands
```bash
# Test scope validation
nighthawk scope

# Test configuration
nighthawk config show

# Test with skip-scope flag (for testing only)
nighthawk web https://example.com --skip-scope
```

---

## 🐳 Docker Installation (Alternative)

### Using Provided Dockerfile

1. **Build Image**
   ```bash
   cd NightHawk
   docker build -t encrypted-crew-nighthawk:2.0.0 .
   ```

2. **Run Container**
   ```bash
   docker run -it --rm \
     -v $(pwd)/scope.yaml:/app/scope.yaml \
     -v $(pwd)/output:/app/output \
     encrypted-crew-nighthawk:2.0.0 \
     nighthawk --version
   ```

3. **Run Assessment**
   ```bash
   docker run -it --rm \
     -v $(pwd)/scope.yaml:/app/scope.yaml \
     -v $(pwd)/output:/app/output \
     encrypted-crew-nighthawk:2.0.0 \
     nighthawk web https://example.com
   ```

---

## 🔄 Updating

### Update from Git

```bash
cd NightHawk
git pull origin main
pip install -e . --force-reinstall
```

### Update from pip

```bash
pip install --upgrade git+https://github.com/Xenoz-GitHub/NightHawk.git
```

---

## 🗑️ Uninstallation

### Remove Package

```bash
pip uninstall nighthawk
```

### Remove Configuration

```bash
# Windows
rmdir /s %USERPROFILE%\.nighthawk

# Linux/macOS
rm -rf ~/.nighthawk
```

### Remove Repository

```bash
# Navigate to parent directory
cd ..
rm -rf NightHawk
```

---

## 📦 Development Installation

For contributing or development:

1. **Clone Repository**
   ```bash
   git clone https://github.com/Xenoz-GitHub/NightHawk.git
   cd NightHawk
   ```

2. **Install with Dev Dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

3. **Install Pre-commit Hooks**
   ```bash
   pre-commit install
   ```

4. **Run Tests**
   ```bash
   pytest
   ```

5. **Run Linter**
   ```bash
   ruff check src/
   ```

6. **Format Code**
   ```bash
   ruff format src/
   ```

---

## 🔍 Dependency Information

### Core Dependencies
- typer >= 0.12.5 (CLI framework)
- rich >= 13.9.0 (Terminal formatting)
- httpx >= 0.27.0 (HTTP client)
- pydantic >= 2.9.0 (Data validation)
- sqlalchemy >= 2.0.35 (Database)
- fastapi >= 0.115.0 (API framework)

### Optional Dependencies
- pytest (testing)
- ruff (linting)
- mypy (type checking)
- pre-commit (git hooks)

### Platform-Specific Dependencies
- **Windows**: colorama (automatic)
- **Linux**: scapy requires libpcap-dev
- **All**: weasyprint requires system fonts

---

## ❓ Common Installation Issues

### Issue: "No module named 'nighthawk'"

**Solution:**
```bash
# Reinstall in editable mode
pip install -e .

# Or use full install
pip install .
```

### Issue: "Command 'nighthawk' not found"

**Solution:**
```bash
# Ensure pip bin directory is in PATH
# Windows
set PATH=%PATH%;%USERPROFILE%\AppData\Roaming\Python\Python311\Scripts

# Linux/macOS
export PATH=$PATH:~/.local/bin

# Or use python -m
python -m nighthawk.cli.main --version
```

### Issue: "SSL/TLS certificate errors"

**Solution:**
```bash
# Update certifi
pip install --upgrade certifi

# Or disable SSL verification (not recommended)
nighthawk web https://example.com --no-verify-ssl
```

### Issue: "Scapy requires root privileges"

**Solution:**
```bash
# Use sudo for network scanning
sudo nighthawk discover 192.168.1.1

# Or grant capabilities
sudo setcap cap_net_raw+ep $(which python)
```

---

## 📞 Getting Help

- **Issues**: https://github.com/Xenoz-GitHub/NightHawk/issues
- **Discussions**: https://github.com/Xenoz-GitHub/NightHawk/discussions
- **Documentation**: See README.md and QUICKSTART.md
- **CLI Help**: `nighthawk --help` or `nighthawk <command> --help`

---

<div align="center">

**ENCRYPTED CREW - NIGHTHAWK v2.0.0**

*Professional Ethical Red-Team Reconnaissance Platform*

Installation complete? Run `nighthawk --version` to get started!

</div>
