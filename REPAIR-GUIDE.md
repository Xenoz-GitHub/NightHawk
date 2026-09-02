# ENCRYPTED CREW - NIGHTHAWK Self-Repair Guide

## 🔧 Automatic Repair & Update Feature

NIGHTHAWK v2.0.0 includes a built-in self-repair command that automatically:
- ✅ Uninstalls the current version
- ✅ Clears pip cache
- ✅ Reinstalls from GitHub repository
- ✅ Optionally cleans user configuration

---

## 🚀 Quick Repair

### Basic Repair (Default Branch)
```bash
nighthawk repair
```

This will:
1. Show you what will happen
2. Ask for confirmation
3. Uninstall current version
4. Clear pip cache
5. Reinstall from `encrypted-crew-v2` branch
6. Ask if you want to remove configuration

### Force Repair (No Prompts)
```bash
nighthawk repair --force
```

Performs repair without any confirmation prompts.

### Repair from Specific Branch
```bash
nighthawk repair --branch main
nighthawk repair --branch encrypted-crew-v2
nighthawk repair --branch development
```

---

## 📋 Complete Repair Commands

### Standard Repair
```bash
# Interactive repair with prompts
nighthawk repair

# Force repair without prompts
nighthawk repair --force

# Repair from main branch
nighthawk repair --branch main

# Force repair from main branch
nighthawk repair --branch main --force
```

### Aliases
```bash
# Short form
nighthawk repair -b main -f
```

---

## 🔍 What Happens During Repair

### Step 1: Pre-Repair Check
```
▓▒░ Self-Repair & Update ░▒▓
Repository: https://github.com/Xenoz-GitHub/NightHawk
Branch: encrypted-crew-v2
Current version: 2.0.0
```

### Step 2: Confirmation (unless --force)
```
⚠ This will:
  1. Uninstall current NIGHTHAWK installation
  2. Clear pip cache
  3. Reinstall from GitHub repository
  4. Remove user configuration (optional)

Continue with repair/update? [y/N]:
```

### Step 3: Uninstall Current Version
```
[●] Uninstalling current version...
[+] Uninstalled current version
```

### Step 4: Clear Cache
```
[●] Clearing pip cache...
[+] Cleared pip cache
```

### Step 5: Reinstall from GitHub
```
[i] Installing from GitHub (this may take a minute)...

[Installation output shows here...]

[+] Successfully installed NIGHTHAWK from GitHub!
[i] Verify installation with: nighthawk --version
```

### Step 6: Optional Config Cleanup
```
Also remove user configuration (~/.nighthawk)? [y/N]:
```

---

## 💡 When to Use Repair

### Use Case 1: Installation Issues
If you're experiencing errors like:
- `ModuleNotFoundError`
- `ImportError`
- Command not found
- Unexpected behavior

**Solution:**
```bash
nighthawk repair --force
```

### Use Case 2: Update to Latest Version
To get the latest features and bug fixes:

**Solution:**
```bash
nighthawk repair
```

### Use Case 3: Switch Branches
To try a different version or branch:

**Solution:**
```bash
nighthawk repair --branch main
nighthawk repair --branch development
```

### Use Case 4: Clean Install
To start fresh with default settings:

**Solution:**
```bash
nighthawk repair --force
# Then manually delete config:
rm -rf ~/.nighthawk  # Linux/macOS
Remove-Item -Recurse -Force $env:USERPROFILE\.nighthawk  # Windows
```

### Use Case 5: Corrupted Installation
If the tool won't start or behaves strangely:

**Solution:**
```bash
nighthawk repair --force
```

---

## 🛠️ Manual Repair (Alternative Method)

If the `repair` command itself is broken, use this manual method:

### Windows PowerShell
```powershell
# Uninstall
pip uninstall nighthawk -y

# Clear cache
pip cache purge

# Remove config (optional)
Remove-Item -Recurse -Force $env:USERPROFILE\.nighthawk -ErrorAction SilentlyContinue

# Reinstall from GitHub
pip install --no-cache-dir git+https://github.com/Xenoz-GitHub/NightHawk.git@encrypted-crew-v2

# Verify
nighthawk --version
```

### Linux/macOS
```bash
# Uninstall
pip uninstall nighthawk -y

# Clear cache
pip cache purge

# Remove config (optional)
rm -rf ~/.nighthawk

# Reinstall from GitHub
pip install --no-cache-dir git+https://github.com/Xenoz-GitHub/NightHawk.git@encrypted-crew-v2

# Verify
nighthawk --version
```

---

## 🔄 Update Workflow

### Check Current Version
```bash
nighthawk --version
```

### Repair/Update
```bash
nighthawk repair
```

### Verify New Version
```bash
nighthawk --version
```

### Test Commands
```bash
nighthawk --help
nighthawk config show
nighthawk scope --create
```

---

## ⚠️ Important Notes

### 1. Configuration Preservation
By default, `repair` keeps your user configuration:
- Theme settings
- Scan preferences
- Report settings

To remove it, answer "yes" when prompted or delete manually.

### 2. Scope Files
The `repair` command does **NOT** affect:
- Your `scope.yaml` files
- Assessment data
- Generated reports

These remain untouched in your working directory.

### 3. Active Virtual Environments
If you're using a virtual environment:
```bash
# Make sure it's activated
source venv/bin/activate  # Linux/macOS
.\venv\Scripts\activate   # Windows

# Then run repair
nighthawk repair
```

### 4. Permission Issues
If you get permission errors:

**Windows:** Run PowerShell as Administrator
```powershell
# Right-click PowerShell → Run as Administrator
nighthawk repair --force
```

**Linux/macOS:** Use appropriate permissions
```bash
# If installed with --user
nighthawk repair

# If installed system-wide (not recommended)
sudo env PATH=$PATH nighthawk repair
```

### 5. Network Issues
If GitHub is unreachable:
- Check your internet connection
- Try again later
- Check GitHub status: https://www.githubstatus.com/

### 6. Branch Availability
Make sure the branch exists before trying to install from it:
- `encrypted-crew-v2` (recommended, latest features)
- `main` (stable release)
- Other branches (check repository)

---

## 🐛 Troubleshooting

### Issue: "Command 'nighthawk' not found" after repair

**Solution:**
```bash
# Ensure Python scripts directory is in PATH
# Then reinstall manually
pip install --no-cache-dir git+https://github.com/Xenoz-GitHub/NightHawk.git@encrypted-crew-v2
```

### Issue: "Permission denied"

**Solution:**
```bash
# Windows: Run as Administrator
# Linux/macOS: Check pip permissions
pip install --user --no-cache-dir git+https://github.com/Xenoz-GitHub/NightHawk.git@encrypted-crew-v2
```

### Issue: "SSL certificate error"

**Solution:**
```bash
# Update certificates
pip install --upgrade certifi

# Try repair again
nighthawk repair
```

### Issue: Repair command hangs

**Solution:**
```bash
# Cancel with Ctrl+C
# Try force mode with verbose output
nighthawk repair --force 2>&1 | tee repair.log
```

### Issue: Installation succeeds but version is wrong

**Solution:**
```bash
# Make sure you're running the right command
which nighthawk  # Linux/macOS
where.exe nighthawk  # Windows

# Reinstall with explicit branch
nighthawk repair --branch encrypted-crew-v2 --force
```

---

## 📊 Repair vs Manual Install

| Method | Speed | Safety | Simplicity | Config Cleanup |
|--------|-------|--------|------------|----------------|
| `nighthawk repair` | ⚡⚡⚡ Fast | ✅ Safe | ✅ One command | 🔧 Optional |
| Manual uninstall + install | ⚡ Slow | ⚠️ Manual steps | ❌ Multiple steps | 🔧 Manual |

---

## 🎯 Best Practices

### 1. Regular Updates
```bash
# Check for updates weekly
nighthawk repair
```

### 2. Before Important Assessments
```bash
# Ensure latest version
nighthawk repair
nighthawk --version
```

### 3. After Git Pull (Developers)
```bash
# If developing locally
cd NightHawk
git pull
pip install -e . --force-reinstall
```

### 4. Fresh Start
```bash
# Complete clean install
nighthawk repair --force
rm -rf ~/.nighthawk
nighthawk config show  # Creates new config
```

---

## 📞 Getting Help

If repair fails or you need assistance:

1. **Check logs**: Save repair output for troubleshooting
   ```bash
   nighthawk repair 2>&1 | tee repair-log.txt
   ```

2. **Try manual method**: See "Manual Repair" section above

3. **Report issue**: 
   - GitHub Issues: https://github.com/Xenoz-GitHub/NightHawk/issues
   - Include: OS, Python version, error messages, repair log

4. **Community support**:
   - GitHub Discussions: https://github.com/Xenoz-GitHub/NightHawk/discussions

---

## 🚀 Quick Reference

```bash
# Basic repair
nighthawk repair

# Force repair (no prompts)
nighthawk repair --force

# Repair from specific branch
nighthawk repair --branch main

# Check version after repair
nighthawk --version

# Verify installation
nighthawk --help
nighthawk config show
```

---

<div align="center">

**ENCRYPTED CREW - NIGHTHAWK Self-Repair**

*One command to fix it all*

🔧 `nighthawk repair` 🔧

Version 2.0.0

</div>
