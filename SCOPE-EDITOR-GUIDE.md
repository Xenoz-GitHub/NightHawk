# 🎯 ENCRYPTED CREW - Scope Editor Guide

## Easy Terminal-Based Scope Management!

No more manual file editing! Manage your scope directly in the terminal.

---

## 🚀 Quick Start

### Option 1: Quick Add (Fastest!)
```bash
# Add your target URL directly
nighthawk scope --add-url https://hyenso-portfolio.vercel.app

# Add a domain
nighthawk scope --add-domain hyenso-portfolio.vercel.app

# Now scan it!
nighthawk web https://hyenso-portfolio.vercel.app
```

### Option 2: Interactive Editor
```bash
# Launch interactive menu
nighthawk scope --edit
```

---

## 📝 All Scope Commands

### Create Scope File
```bash
nighthawk scope --create
```
Creates example `scope.yaml` with templates.

### Interactive Editor
```bash
nighthawk scope --edit
```
Opens full-featured editor in terminal:
- Add domains, IPs, CIDRs, URLs
- View all entries
- Remove entries
- Save or cancel

### Quick Add Commands
```bash
# Add domain
nighthawk scope --add-domain example.com

# Add IP address  
nighthawk scope --add-ip 192.168.1.1

# Add URL
nighthawk scope --add-url https://example.com
```

### View Scope
```bash
# Show scope file with syntax highlighting
nighthawk scope --show

# Validate scope
nighthawk scope
```

---

## 🎮 Interactive Editor Usage

### Launch Editor
```bash
nighthawk scope --edit
```

### Menu Options

```
═══ Current Scope ═══
  ● Domains: 0
  ● IPs: 0
  ● CIDRs: 0
  ● URLs: 0

Options:
  1 - Add domain        5 - View all entries
  2 - Add IP           6 - Remove entry
  3 - Add CIDR         7 - Save and exit
  4 - Add URL          8 - Exit without saving

Choose option:
```

### Example Session

```bash
nighthawk scope --edit

# Choose 4 to add URL
Choose option: 4
Enter URL: https://hyenso-portfolio.vercel.app
[+] Added URL: https://hyenso-portfolio.vercel.app

# Choose 1 to add domain
Choose option: 1
Enter domain: hyenso-portfolio.vercel.app
[+] Added domain: hyenso-portfolio.vercel.app

# Choose 5 to view all
Choose option: 5

═══ All Entries ═══

URLs:
  1. https://hyenso-portfolio.vercel.app

Domains:
  1. hyenso-portfolio.vercel.app

# Choose 7 to save
Choose option: 7
[+] Saved scope to: scope.yaml
```

---

## 💡 Real-World Examples

### Example 1: Add Your Website
```bash
# Quick method
nighthawk scope --add-url https://hyenso-portfolio.vercel.app

# Verify it was added
nighthawk scope --show

# Scan it
nighthawk web https://hyenso-portfolio.vercel.app
```

### Example 2: Add Multiple Targets
```bash
# Using interactive editor
nighthawk scope --edit

# In editor:
# 1. Choose option 4, add https://site1.com
# 2. Choose option 4, add https://site2.com  
# 3. Choose option 1, add site3.com
# 4. Choose option 7 to save

# Or using quick commands
nighthawk scope --add-url https://site1.com
nighthawk scope --add-url https://site2.com
nighthawk scope --add-domain site3.com
```

### Example 3: Remove Wrong Entry
```bash
# Use interactive editor
nighthawk scope --edit

# Choose option 6 (Remove entry)
# Choose category (1-4)
# Enter number to remove
# Choose option 7 to save
```

### Example 4: View Current Scope
```bash
# Pretty print with syntax highlighting
nighthawk scope --show

# Or validate scope
nighthawk scope
```

---

## 🎯 Workflow: Start to Scan

### Complete Workflow
```bash
# Step 1: Add your target
nighthawk scope --add-url https://hyenso-portfolio.vercel.app

# Step 2: Verify it was added
nighthawk scope

# Step 3: Run scan
nighthawk web https://hyenso-portfolio.vercel.app

# Done! ✅
```

### Alternative: Interactive
```bash
# Step 1: Open editor
nighthawk scope --edit

# Step 2: Add targets (use menu options 1-4)

# Step 3: Save (option 7)

# Step 4: Run assessment
nighthawk assess
```

---

## 📊 Command Comparison

| Command | Speed | Best For |
|---------|-------|----------|
| `--add-url` | ⚡⚡⚡ Fastest | Single target |
| `--add-domain` | ⚡⚡⚡ Fastest | Single domain |
| `--edit` | ⚡⚡ Medium | Multiple targets, reviewing |
| `--create` | ⚡ Slow | First time setup |

---

## 🔧 Advanced Usage

### Add from Different Directory
```bash
nighthawk scope --file ~/my-project/scope.yaml --add-url https://example.com
```

### Multiple Operations
```bash
# Add several targets
nighthawk scope --add-domain example.com
nighthawk scope --add-domain api.example.com
nighthawk scope --add-ip 192.168.1.1

# View all
nighthawk scope --show
```

### Check Before Editing
```bash
# See what's there
nighthawk scope --show

# Then edit
nighthawk scope --edit
```

---

## ⚠️ Important Notes

### Scope File Location
By default, scope.yaml is created/edited in current directory.

```bash
# Check current directory
pwd  # Linux/macOS
cd   # Windows

# Create scope in current directory
nighthawk scope --create
```

### Wildcard Domains
```bash
# In interactive editor or manually:
*.example.com      # Matches all subdomains
test.*.example.com # Matches test.[anything].example.com
```

### URL Format
Always include protocol:
- ✅ Good: `https://example.com`
- ✅ Good: `http://192.168.1.1`
- ❌ Bad: `example.com` (use --add-domain instead)
- ❌ Bad: `www.example.com` (use --add-domain instead)

---

## 🐛 Troubleshooting

### Issue: "Scope file not found"
**Solution:**
```bash
# Create it first
nighthawk scope --create

# Or use --edit (creates automatically)
nighthawk scope --edit
```

### Issue: "Already exists" warning
**Solution:**
```bash
# View current entries
nighthawk scope --show

# Remove duplicates with editor
nighthawk scope --edit
# Choose option 6 (Remove)
```

### Issue: Changes not saving
**Solution:**
Make sure you choose option 7 (Save and exit) in the editor, not option 8 (Exit without saving).

### Issue: Can't find scope.yaml
**Solution:**
```bash
# Show full path
nighthawk scope --show
# Or create in current directory
nighthawk scope --create
```

---

## 💻 Terminal Commands Summary

```bash
# Quick Commands
nighthawk scope --create                    # Create example
nighthawk scope --edit                      # Interactive editor
nighthawk scope --show                      # View file
nighthawk scope                             # Validate

# Quick Add
nighthawk scope --add-domain <domain>       # Add domain
nighthawk scope --add-ip <ip>               # Add IP
nighthawk scope --add-url <url>             # Add URL

# Your Use Case
nighthawk scope --add-url https://hyenso-portfolio.vercel.app
nighthawk web https://hyenso-portfolio.vercel.app
```

---

## 🎉 Best Practices

### 1. Start Simple
```bash
# Just add what you need
nighthawk scope --add-url https://your-site.com
nighthawk web https://your-site.com
```

### 2. Review Before Scanning
```bash
# Check your scope
nighthawk scope --show

# Validate
nighthawk scope
```

### 3. Use Interactive for Multiple Targets
```bash
# When adding 3+ targets
nighthawk scope --edit
```

### 4. Keep Backups
```bash
# Copy your scope
cp scope.yaml scope.backup.yaml  # Linux/macOS
copy scope.yaml scope.backup.yaml  # Windows
```

---

<div align="center">

**ENCRYPTED CREW - NIGHTHAWK**

*Terminal-Based Scope Management*

🎯 No more manual file editing! 🎯

```bash
nighthawk scope --edit
nighthawk scope --add-url <your-target>
```

Version 2.0.0 | Commit: 18fd528

https://github.com/Xenoz-GitHub/NightHawk

</div>
