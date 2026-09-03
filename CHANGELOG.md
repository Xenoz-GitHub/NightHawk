# ENCRYPTED CREW - NIGHTHAWK Changelog

All notable changes to this project are documented in this file.

## [2.0.0] - 2026-09-02

###  **ENCRYPTED CREW BRANDING**
- Added professional "ENCRYPTED CREW" ASCII art banner
- Implemented cyberpunk-inspired color scheme (green/cyan/red/yellow)
- Created Windows-compatible fallback ASCII banners
- Added unicode detection with automatic fallback for legacy systems

###  **Major Features Added**
- **User Configuration System**: Complete preferences management
  - Theme customization (colors, banner visibility, emoji usage)
  - Scan configuration (timeouts, threading, rate limiting)
  - Report settings (formats, redaction, timestamps)
  - Global settings (scope enforcement, verbosity, logging)
  - `nighthawk config` command for managing settings

- **Optional Scope Validation**: `--skip-scope` flag added to all commands
  - Allows bypassing scope.yaml requirement (with warnings)
  - Better error messages guiding users to create scope files
  - `nighthawk scope --create` for easy scope file generation

- **Export Functionality**: JSON export for all assessment types
  - `--export` flag on web, tech, and secrets commands
  - Structured JSON output for further analysis
  - Integration-ready format for CI/CD pipelines

- **Enhanced Error Handling**:
  - Graceful handling of missing dependencies
  - Clear, actionable error messages
  - Helpful suggestions for resolving issues
  - Keyboard interrupt handling (Ctrl+C)

###  **Critical Bug Fixes**
- **Fixed `--version` flag**: No longer requires a command
  - Changed `no_args_is_help=False` in CLI definition
  - Proper version display with full banner
  - Added `--banner` flag for standalone banner display

- **Fixed Windows Console Encoding Issues**:
  - Automatic UTF-8 detection and fallback
  - ASCII-safe characters for all UI elements
  - Compatible with Windows PowerShell and CMD
  - No more `UnicodeEncodeError` exceptions

- **Fixed Scope Requirement Issues**:
  - Commands no longer fail silently
  - Clear guidance on creating scope files
  - Option to bypass for testing/development

###  **UI/UX Improvements**

#### Visual Enhancements
- Professional header panels for all commands
- Color-coded status indicators ([+], [-], [!], [i])
- Styled progress indicators and spinners
- Rich tables with borders and formatting
- Context-aware color coding (success=green, error=red, warning=yellow)

#### Command Output
- **Web Assessment**: Detailed security header analysis, TLS info, categorized findings
- **Network Discovery**: Port/service/version tables with risk-based coloring
- **Technology Detection**: Confidence scoring with visual indicators, category icons
- **Secret Scanning**: Redacted output, type-based summaries, risk assessment
- **Assessment Campaigns**: Progress tracking, target-by-target status updates

###  **Global Compatibility**
- **Windows**: Full PowerShell and CMD support, UTF-8 handling, path compatibility
- **Linux/macOS**: Enhanced with all new features
- **Cross-platform**: Consistent behavior across operating systems
- **Terminal Support**: Works with legacy and modern terminals

###  **Documentation**
- **README.md**: Comprehensive 500+ line documentation
  - Feature overview with visual elements
  - Complete command reference
  - Usage examples and workflows
  - Security and ethical guidelines
  - Development setup instructions

- **QUICKSTART.md**: Step-by-step getting started guide
  - 3 installation options
  - First-time setup instructions
  - Common workflows and examples
  - Troubleshooting section

- **Example Configuration**: `.nighthawk/config.example.json`
  - All available settings documented
  - Sensible defaults provided
  - Copy-paste ready for customization

###  **Technical Improvements**
- Pydantic v2 models for configuration
- Type-safe settings management
- Modular banner system
- Improved import structure
- Better separation of concerns

###  **Configuration Options**

#### Theme
- Customizable colors for all UI elements
- Banner visibility toggle
- Emoji/icon usage toggle

#### Scanning
- Configurable timeouts
- Thread pool sizing
- Rate limiting
- SSL verification toggle
- Custom user agents

#### Reporting
- Default format selection (HTML/JSON/CSV)
- Raw data inclusion toggle
- Secret redaction control
- Timestamp format customization

#### Global
- Auto scope creation
- Strict scope enforcement
- Verbose output mode
- Log level configuration
- Default paths and directories

###  **Command Additions**
```bash
nighthawk --version          # Show version with banner
nighthawk --banner           # Display full ASCII banner
nighthawk config show        # View configuration
nighthawk config set         # Modify settings
nighthawk config reset       # Reset to defaults
nighthawk config export      # Export example config
nighthawk scope --create     # Create scope template
```

###  **Security Enhancements**
- Maintained all security boundaries from v1.0.0
- Added warning indicators for bypassed safety features
- Enhanced scope validation feedback
- Default secret redaction in all outputs
- Ethical usage reminders in banner and docs

###  **Command-Specific Improvements**

#### `nighthawk scope`
- Interactive scope creation
- Overwrite confirmation prompts
- Detailed validation output
- Example scope with comments

#### `nighthawk web`
- Security header analysis table
- TLS/SSL detailed information
- Status code color coding
- Export to JSON option

#### `nighthawk discover`
- Port range customization
- Service-based color coding
- Timeout configuration
- Result count summary

#### `nighthawk tech`
- Confidence level visualization
- Category icons (if emoji enabled)
- Sorted by confidence
- Evidence truncation

#### `nighthawk secrets`
- Type-based grouping
- Confidence-based color coding
- Optional redaction toggle
- Limit display with export option

#### `nighthawk assess`
- Module selection
- Per-target progress
- Error recovery
- Result compilation

#### `nighthawk report`
- Format selection (HTML/JSON/CSV)
- File size reporting
- Absolute path display
- Campaign ID support

#### `nighthawk config`
- Nested configuration display
- Dot-notation key access
- JSON value parsing
- Reset with confirmation

###  **Breaking Changes**
- Configuration file format changed to JSON (from YAML if existed)
- Some CLI flags renamed for consistency
- Default output format locations changed
- Minimum Python version clarified (3.11+)

###  **Package Information**
- Version: 2.0.0
- Python: 3.11+
- Author: ENCRYPTED CREW
- License: MIT
- Repository: https://github.com/Xenoz-GitHub/NightHawk

###  **Credits**
- Original NightHawk project by Xenoz-GitHub
- Enhanced and branded by ENCRYPTED CREW
- Community feedback and testing

---

## [1.0.0] - Previous Release

### Initial Release
- Basic CLI framework
- Scope management
- Network scanning
- Web assessment
- Technology fingerprinting
- Secret scanning
- Report generation
- FastAPI backend
- React frontend

### Known Issues (Fixed in 2.0.0)
- `--version` flag required command argument
- Windows console encoding errors
- Missing scope.yaml caused unclear errors
- Limited configuration options
- Basic UI without colors/formatting

---

## Future Roadmap

### Planned for v2.1.0
- Interactive wizard mode for scope creation
- Progress persistence across sessions
- Enhanced report templates
- API endpoint testing
- Vulnerability correlation engine
- Dashboard improvements

### Planned for v2.2.0
- Plugin system for custom scanners
- CI/CD integrations (GitHub Actions, GitLab CI)
- Bulk target import from files
- Historical comparison reports
- Advanced filtering and search

### Planned for v3.0.0
- Machine learning for vulnerability prediction
- Automated remediation suggestions
- Integration with major security tools
- Cloud-native deployment options
- Advanced correlation and risk scoring

---

<div align="center">

**ENCRYPTED CREW - NIGHTHAWK**

*Professional Ethical Red-Team Reconnaissance Platform*

Version 2.0.0 | September 2, 2026

</div>
