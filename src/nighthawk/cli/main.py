"""ENCRYPTED CREW - NIGHTHAWK CLI main entry point."""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from pathlib import Path
import sys

from nighthawk import __version__
from nighthawk.cli.banner import (
    print_banner,
    print_success,
    print_error,
    print_warning,
    print_info,
    create_header_panel,
    create_status_text,
)

console = Console()

app = typer.Typer(
    name="nighthawk",
    help="ENCRYPTED CREW — NIGHTHAWK Ethical Red-Team Reconnaissance Platform",
    add_completion=False,
    no_args_is_help=False,  # Changed to False to allow --version without command
    rich_markup_mode="rich",
)


@app.callback(invoke_without_command=True)
def main_callback(
    ctx: typer.Context,
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Show version and exit.",
    ),
    banner: bool = typer.Option(
        False,
        "--banner",
        "-b",
        help="Show full banner.",
    ),
) -> None:
    """ENCRYPTED CREW - NIGHTHAWK Ethical Red-Team Reconnaissance Platform."""
    # Handle --version flag
    if version:
        print_banner(console, __version__)
        console.print()
        print_info(console, f"Version: {__version__}")
        print_info(console, "Platform: Ethical Red-Team Reconnaissance & Attack-Surface Assessment")
        print_info(console, "Author: ENCRYPTED CREW")
        console.print()
        console.print("[dim]For help, use: [cyan]nighthawk --help[/cyan][/dim]")
        raise typer.Exit()
    
    # Handle --banner flag
    if banner:
        print_banner(console, __version__)
        raise typer.Exit()
    
    # If no subcommand, show help with banner
    if ctx.invoked_subcommand is None:
        print_banner(console, __version__)
        console.print(ctx.get_help())
        raise typer.Exit()


@app.command()
def scope(
    file: str = typer.Option("scope.yaml", "--file", "-f", help="Scope configuration file."),
    create: bool = typer.Option(False, "--create", "-c", help="Create example scope.yaml file."),
) -> None:
    """Validate or create scope configuration."""
    from nighthawk.scope.manager import ScopeManager
    from nighthawk.core.exceptions import ConfigurationError
    
    console.print(create_header_panel("Scope Management", "Authorization & Target Configuration"))
    console.print()
    
    # Create example scope if requested
    if create:
        if Path(file).exists():
            print_warning(console, f"File already exists: {file}")
            overwrite = typer.confirm("Overwrite existing file?")
            if not overwrite:
                print_info(console, "Operation cancelled")
                raise typer.Exit(0)
        
        example_scope = """# ENCRYPTED CREW - NIGHTHAWK Scope Configuration
# Define authorized targets for ethical security assessment

# Authorized domains
domains:
  - example.com
  - test.example.com
  - "*.dev.example.com"

# Authorized IP addresses
ips:
  - 192.168.1.1
  - 10.0.0.1

# Authorized CIDR ranges
cidrs:
  - 192.168.1.0/24
  - 10.0.0.0/16

# URLs (optional)
urls:
  - https://example.com
  - https://api.example.com

# Git repositories (optional)
repositories:
  - https://github.com/yourusername/your-repo

# Authorized assessment modules
modules:
  - web
  - network
  - secrets
  - technology
  - dns

# Assessment metadata
metadata:
  project: "Security Assessment"
  authorized_by: "Security Team"
  date: "2026-09-02"
  scope_type: "External"
"""
        Path(file).write_text(example_scope, encoding="utf-8")
        print_success(console, f"Created example scope file: {file}")
        print_info(console, "Edit the file to add your authorized targets")
        raise typer.Exit(0)
    
    # Validate existing scope
    try:
        if not Path(file).exists():
            print_error(console, f"Scope file not found: {file}")
            print_info(console, f"Create one with: [cyan]nighthawk scope --create[/cyan]")
            raise typer.Exit(1)
        
        manager = ScopeManager(file)
        
        # Create validation table
        table = Table(title="✓ Scope Configuration Valid", border_style="green")
        table.add_column("Category", style="cyan", no_wrap=True)
        table.add_column("Values", style="white")
        
        table.add_row("📁 Config File", str(Path(file).absolute()))
        table.add_row("🌐 Domains", str(len(manager.config.domains)) if manager.config.domains else "0")
        table.add_row("🖥️  IP Addresses", str(len(manager.config.ips)) if manager.config.ips else "0")
        table.add_row("📡 CIDR Ranges", str(len(manager.config.cidrs)) if manager.config.cidrs else "0")
        table.add_row("🔧 Authorized Modules", ", ".join(manager.get_authorized_modules()))
        
        console.print(table)
        console.print()
        
        # Show details
        if manager.config.domains:
            print_info(console, f"Domains: {', '.join(manager.config.domains[:5])}")
        if manager.config.ips:
            print_info(console, f"IPs: {', '.join(manager.config.ips[:5])}")
        if manager.config.cidrs:
            print_info(console, f"CIDRs: {', '.join(manager.config.cidrs[:5])}")
        
        print_success(console, "Scope configuration is valid and ready to use")
        
    except ConfigurationError as exc:
        print_error(console, f"Invalid scope configuration: {exc}")
        raise typer.Exit(1)
    except Exception as exc:
        print_error(console, f"Unexpected error: {exc}")
        raise typer.Exit(1)


@app.command()
def discover(
    target: str = typer.Argument(..., help="IP, CIDR, or hostname to discover."),
    scope_file: str = typer.Option("scope.yaml", "--scope", "-s", help="Scope configuration file."),
    ports: str = typer.Option("1-1000", "--ports", "-p", help="Port range to scan (e.g., 1-1000, 80,443)."),
    timeout: int = typer.Option(5, "--timeout", "-t", help="Connection timeout in seconds."),
    skip_scope: bool = typer.Option(False, "--skip-scope", help="Skip scope validation (use with caution)."),
) -> None:
    """Discover authorized network assets and services."""
    from nighthawk.scope.manager import ScopeManager
    from nighthawk.network.scanner import NetworkScanner
    import asyncio
    
    console.print(create_header_panel("Network Discovery", f"Target: {target}"))
    console.print()
    
    try:
        # Handle scope validation
        scope = None
        if not skip_scope:
            scope_path = Path(scope_file)
            if not scope_path.exists():
                print_warning(console, f"Scope file not found: {scope_file}")
                print_info(console, "Create one with: [cyan]nighthawk scope --create[/cyan]")
                print_info(console, "Or use [yellow]--skip-scope[/yellow] to bypass (not recommended)")
                raise typer.Exit(1)
            
            scope = ScopeManager(scope_file)
            scope.validate_target(target)
            print_success(console, f"Target authorized: {target}")
        else:
            print_warning(console, "⚠️  Scope validation SKIPPED - Ensure you have authorization!")
        
        print_info(console, f"Scanning ports: {ports}")
        print_info(console, f"Timeout: {timeout}s")
        console.print()
        
        # Run scan
        with console.status("[bold cyan]Scanning network...[/bold cyan]", spinner="dots"):
            scanner = NetworkScanner()
            result = asyncio.run(scanner.run(target, scope_manager=scope))
        
        # Display results
        results_list = result.get("results", [])
        
        if not results_list:
            print_warning(console, "No open ports discovered")
            raise typer.Exit(0)
        
        table = Table(
            title=f"🔍 Network Scan Results: {target}",
            border_style="cyan",
            show_lines=True
        )
        table.add_column("Port", style="bold cyan", justify="right")
        table.add_column("State", style="bold green")
        table.add_column("Service", style="white")
        table.add_column("Version", style="dim white")
        
        for r in results_list:
            port = str(r.get("port", ""))
            state = r.get("state", "")
            service = r.get("service", "unknown")
            version = r.get("version", "")
            
            # Color code by service
            service_style = "white"
            if service in ["http", "https"]:
                service_style = "green"
            elif service in ["ssh", "telnet"]:
                service_style = "yellow"
            elif service in ["ftp", "smb"]:
                service_style = "red"
            
            table.add_row(port, state, f"[{service_style}]{service}[/{service_style}]", version)
        
        console.print(table)
        console.print()
        print_success(console, f"Discovered {len(results_list)} open port(s)")
        
    except KeyboardInterrupt:
        print_warning(console, "Scan cancelled by user")
        raise typer.Exit(130)
    except Exception as exc:
        print_error(console, f"Discovery failed: {exc}")
        raise typer.Exit(1)


@app.command()
def web(
    url: str = typer.Argument(..., help="Target URL or domain."),
    scope_file: str = typer.Option("scope.yaml", "--scope", "-s", help="Scope configuration file."),
    skip_scope: bool = typer.Option(False, "--skip-scope", help="Skip scope validation (use with caution)."),
    follow_redirects: bool = typer.Option(True, "--follow-redirects/--no-redirects", help="Follow HTTP redirects."),
    timeout: int = typer.Option(30, "--timeout", "-t", help="Request timeout in seconds."),
    export: str = typer.Option(None, "--export", "-e", help="Export results to JSON file."),
) -> None:
    """Assess website security, headers, and TLS configuration."""
    from nighthawk.scope.manager import ScopeManager
    from nighthawk.web.scanner import WebScanner
    import asyncio
    import json
    
    console.print(create_header_panel("Web Security Assessment", f"Target: {url}"))
    console.print()
    
    try:
        # Handle scope validation
        scope = None
        if not skip_scope:
            scope_path = Path(scope_file)
            if not scope_path.exists():
                print_warning(console, f"Scope file not found: {scope_file}")
                print_info(console, "Create one with: [cyan]nighthawk scope --create[/cyan]")
                print_info(console, "Or use [yellow]--skip-scope[/yellow] to bypass (not recommended)")
                raise typer.Exit(1)
            
            scope = ScopeManager(scope_file)
            scope.validate_target(url)
            print_success(console, f"Target authorized: {url}")
        else:
            print_warning(console, "⚠️  Scope validation SKIPPED - Ensure you have authorization!")
        
        console.print()
        
        # Run scan
        with console.status("[bold cyan]Scanning website...[/bold cyan]", spinner="dots"):
            scanner = WebScanner()
            result = asyncio.run(scanner.run(url, scope_manager=scope))
        
        # Display results
        console.print(Panel.fit(
            f"[bold white]Web Assessment Complete[/bold white]\n"
            f"[cyan]URL:[/cyan] {url}",
            border_style="green"
        ))
        console.print()
        
        # Status and basic info
        status_code = result.get('status_code', 'N/A')
        status_color = "green" if str(status_code).startswith("2") else "yellow" if str(status_code).startswith("3") else "red"
        
        info_table = Table(border_style="cyan", show_header=False, box=None)
        info_table.add_column("Property", style="cyan")
        info_table.add_column("Value", style="white")
        
        info_table.add_row("📊 Status Code", f"[{status_color}]{status_code}[/{status_color}]")
        info_table.add_row("📋 Content Type", result.get('content_type', 'N/A'))
        info_table.add_row("📏 Content Length", str(result.get('content_length', 'N/A')))
        info_table.add_row("🔒 TLS/SSL", "✓ Supported" if result.get('tls', {}).get('supported', False) else "✗ Not detected")
        info_table.add_row("🔀 Redirects", str(len(result.get('redirect_chain', []))))
        info_table.add_row("📑 Headers", str(len(result.get('headers', {}))))
        
        console.print(info_table)
        console.print()
        
        # Security headers analysis
        security_headers = result.get('security_headers', {})
        if security_headers:
            sec_table = Table(title="🛡️  Security Headers Analysis", border_style="cyan")
            sec_table.add_column("Header", style="cyan")
            sec_table.add_column("Status", style="white")
            sec_table.add_column("Value", style="dim white")
            
            important_headers = [
                'strict-transport-security',
                'content-security-policy',
                'x-frame-options',
                'x-content-type-options',
                'x-xss-protection',
                'referrer-policy',
            ]
            
            headers = result.get('headers', {})
            for header in important_headers:
                if header in headers:
                    sec_table.add_row(
                        header,
                        "[green]✓ Present[/green]",
                        str(headers[header])[:50] + "..." if len(str(headers[header])) > 50 else str(headers[header])
                    )
                else:
                    sec_table.add_row(header, "[red]✗ Missing[/red]", "")
            
            console.print(sec_table)
            console.print()
        
        # TLS information
        tls_info = result.get('tls', {})
        if tls_info.get('supported'):
            print_success(console, f"TLS Version: {tls_info.get('version', 'Unknown')}")
            print_info(console, f"Cipher Suite: {tls_info.get('cipher', 'Unknown')}")
        
        # Export if requested
        if export:
            export_path = Path(export)
            export_path.write_text(json.dumps(result, indent=2), encoding='utf-8')
            print_success(console, f"Results exported to: {export}")
        
        print_success(console, "Web assessment complete")
        
    except KeyboardInterrupt:
        print_warning(console, "Scan cancelled by user")
        raise typer.Exit(130)
    except Exception as exc:
        print_error(console, f"Web scan failed: {exc}")
        raise typer.Exit(1)


@app.command()
def tech(
    url: str = typer.Argument(..., help="Target URL or domain for technology detection."),
    scope_file: str = typer.Option("scope.yaml", "--scope", "-s", help="Scope configuration file."),
    skip_scope: bool = typer.Option(False, "--skip-scope", help="Skip scope validation (use with caution)."),
    export: str = typer.Option(None, "--export", "-e", help="Export results to JSON file."),
) -> None:
    """Detect website technologies and frameworks."""
    from nighthawk.scope.manager import ScopeManager
    from nighthawk.web.scanner import WebScanner
    from nighthawk.technology.scanner import FingerprintEngine
    import asyncio
    import json
    
    console.print(create_header_panel("Technology Fingerprinting", f"Target: {url}"))
    console.print()
    
    try:
        # Handle scope validation
        scope = None
        if not skip_scope:
            scope_path = Path(scope_file)
            if not scope_path.exists():
                print_warning(console, f"Scope file not found: {scope_file}")
                print_info(console, "Create one with: [cyan]nighthawk scope --create[/cyan]")
                print_info(console, "Or use [yellow]--skip-scope[/yellow] to bypass (not recommended)")
                raise typer.Exit(1)
            
            scope = ScopeManager(scope_file)
            scope.validate_target(url)
            print_success(console, f"Target authorized: {url}")
        else:
            print_warning(console, "⚠️  Scope validation SKIPPED - Ensure you have authorization!")
        
        console.print()
        
        # Run scan
        with console.status("[bold cyan]Detecting technologies...[/bold cyan]", spinner="dots"):
            scanner = WebScanner()
            web_result = asyncio.run(scanner.run(url, scope_manager=scope))
            
            engine = FingerprintEngine()
            evidence = {
                "headers": web_result.get("headers", {}),
                "html_text": web_result.get("content_type", ""),
                "cookies": web_result.get("cookies", []),
                "paths": [url],
            }
            matches = engine.match_technology(evidence)
        
        if not matches:
            print_warning(console, "No technologies detected")
            raise typer.Exit(0)
        
        # Display results
        table = Table(
            title=f"🔍 Technology Matches: {url}",
            border_style="cyan",
            show_lines=True
        )
        table.add_column("Technology", style="bold cyan", no_wrap=True)
        table.add_column("Category", style="green")
        table.add_column("Confidence", style="yellow", justify="center")
        table.add_column("Evidence", style="dim white")
        
        for m in sorted(matches, key=lambda x: x.confidence_level.value, reverse=True):
            # Color code confidence
            conf_value = m.confidence_level.value
            if conf_value == "high":
                conf_display = "[bold green]●●● HIGH[/bold green]"
            elif conf_value == "medium":
                conf_display = "[bold yellow]●●○ MEDIUM[/bold yellow]"
            else:
                conf_display = "[dim]●○○ LOW[/dim]"
            
            # Category icon
            category_icons = {
                "framework": "🏗️",
                "cms": "📝",
                "server": "🖥️",
                "language": "💻",
                "library": "📚",
                "analytics": "📊",
                "security": "🔒",
            }
            icon = category_icons.get(m.category.lower(), "🔧")
            
            evidence_str = ", ".join(m.evidence[:3])
            if len(evidence_str) > 60:
                evidence_str = evidence_str[:57] + "..."
            
            table.add_row(
                m.name,
                f"{icon} {m.category}",
                conf_display,
                evidence_str
            )
        
        console.print(table)
        console.print()
        print_success(console, f"Detected {len(matches)} technology/technologies")
        
        # Export if requested
        if export:
            export_data = [
                {
                    "technology": m.name,
                    "category": m.category,
                    "confidence": m.confidence_level.value,
                    "evidence": m.evidence,
                }
                for m in matches
            ]
            export_path = Path(export)
            export_path.write_text(json.dumps(export_data, indent=2), encoding='utf-8')
            print_success(console, f"Results exported to: {export}")
        
    except KeyboardInterrupt:
        print_warning(console, "Detection cancelled by user")
        raise typer.Exit(130)
    except Exception as exc:
        print_error(console, f"Technology detection failed: {exc}")
        raise typer.Exit(1)


@app.command()
def secrets(
    path: str = typer.Argument(".", help="Path to codebase or repository."),
    scope_file: str = typer.Option("scope.yaml", "--scope", "-s", help="Scope configuration file."),
    skip_scope: bool = typer.Option(False, "--skip-scope", help="Skip scope validation (use with caution)."),
    export: str = typer.Option(None, "--export", "-e", help="Export results to JSON file."),
    redact: bool = typer.Option(True, "--redact/--no-redact", help="Redact sensitive values in output."),
) -> None:
    """Scan authorized source code for potential secret exposure."""
    from nighthawk.scope.manager import ScopeManager
    from nighthawk.secrets.scanner import SecretScanner
    import asyncio
    import json
    
    console.print(create_header_panel("Secret Scanner", f"Path: {path}"))
    console.print()
    
    try:
        # Handle scope validation
        scope = None
        if not skip_scope:
            scope_path = Path(scope_file)
            if not scope_path.exists():
                print_warning(console, f"Scope file not found: {scope_file}")
                print_info(console, "Create one with: [cyan]nighthawk scope --create[/cyan]")
                print_info(console, "Or use [yellow]--skip-scope[/yellow] to bypass (not recommended)")
                raise typer.Exit(1)
            
            scope = ScopeManager(scope_file)
            scope.validate_target(path)
            print_success(console, f"Target authorized: {path}")
        else:
            print_warning(console, "⚠️  Scope validation SKIPPED - Ensure you have authorization!")
        
        if not redact:
            print_warning(console, "⚠️  Redaction DISABLED - Secrets will be visible in output!")
        
        console.print()
        
        # Run scan
        with console.status("[bold cyan]Scanning for secrets...[/bold cyan]", spinner="dots"):
            scanner = SecretScanner()
            result = asyncio.run(scanner.run(path, scope_manager=scope))
        
        findings = result.get("findings", [])
        
        if not findings:
            print_success(console, "No potential secrets detected")
            raise typer.Exit(0)
        
        # Display results
        table = Table(
            title=f"🔐 Potential Secret Findings ({len(findings)})",
            border_style="red",
            show_lines=True
        )
        table.add_column("File", style="cyan", no_wrap=True)
        table.add_column("Line", style="yellow", justify="right")
        table.add_column("Type", style="red")
        table.add_column("Confidence", style="yellow", justify="center")
        table.add_column("Match", style="dim white")
        
        for f in findings[:20]:  # Limit to 20 for display
            file_path = str(f.get("file", ""))
            file_name = Path(file_path).name if file_path else "unknown"
            
            match_value = f.get("match", "")
            if redact and len(match_value) > 10:
                match_value = match_value[:3] + "***" + match_value[-3:]
            elif len(match_value) > 50:
                match_value = match_value[:47] + "..."
            
            confidence = f.get('confidence', 0)
            conf_color = "red" if confidence > 0.8 else "yellow" if confidence > 0.5 else "white"
            
            table.add_row(
                file_name,
                str(f.get("line", "")),
                f.get("type", "unknown"),
                f"[{conf_color}]{confidence:.2f}[/{conf_color}]",
                match_value
            )
        
        console.print(table)
        console.print()
        
        if len(findings) > 20:
            print_info(console, f"Showing 20 of {len(findings)} findings. Use --export to see all.")
        
        # Summary by type
        type_counts = {}
        for f in findings:
            secret_type = f.get("type", "unknown")
            type_counts[secret_type] = type_counts.get(secret_type, 0) + 1
        
        print_warning(console, f"Total findings: {len(findings)}")
        for secret_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
            print_info(console, f"  {secret_type}: {count}")
        
        # Export if requested
        if export:
            export_path = Path(export)
            export_path.write_text(json.dumps(findings, indent=2), encoding='utf-8')
            print_success(console, f"Results exported to: {export}")
        
    except KeyboardInterrupt:
        print_warning(console, "Scan cancelled by user")
        raise typer.Exit(130)
    except Exception as exc:
        print_error(console, f"Secret scan failed: {exc}")
        raise typer.Exit(1)


@app.command()
def assess(
    scope_file: str = typer.Option("scope.yaml", "--scope", "-s", help="Scope configuration file."),
    modules: str = typer.Option("all", "--modules", "-m", help="Comma-separated modules to run (web,network,secrets,tech)."),
) -> None:
    """Run a full assessment campaign across all authorized targets."""
    from nighthawk.scope.manager import ScopeManager
    from nighthawk.orchestrator.campaign import AssessmentCampaign
    from nighthawk.network.scanner import NetworkScanner
    from nighthawk.web.scanner import WebScanner
    import asyncio
    import uuid
    
    console.print(create_header_panel("Full Assessment Campaign", "Comprehensive Security Assessment"))
    console.print()
    
    try:
        # Load scope
        if not Path(scope_file).exists():
            print_error(console, f"Scope file not found: {scope_file}")
            print_info(console, "Create one with: [cyan]nighthawk scope --create[/cyan]")
            raise typer.Exit(1)
        
        scope = ScopeManager(scope_file)
        print_success(console, f"Loaded scope: {scope_file}")
        
        # Parse modules
        if modules.lower() == "all":
            selected_modules = ["web", "network", "secrets", "tech"]
        else:
            selected_modules = [m.strip() for m in modules.split(",")]
        
        print_info(console, f"Selected modules: {', '.join(selected_modules)}")
        console.print()
        
        # Create campaign
        campaign = AssessmentCampaign(str(uuid.uuid4()), scope)
        
        console.print(Panel.fit(
            f"[bold green]Campaign Started[/bold green]\n"
            f"[cyan]Campaign ID:[/cyan] {campaign.campaign_id}",
            border_style="cyan"
        ))
        console.print()
        
        # Get targets
        targets = scope.config.domains or scope.config.ips or []
        if not targets:
            print_warning(console, "No targets defined in scope")
            raise typer.Exit(1)
        
        print_info(console, f"Targets: {len(targets)}")
        
        # Run assessment
        for idx, target in enumerate(targets[:10], 1):  # Limit to 10 targets
            console.print(f"\n[bold cyan]Target {idx}/{min(len(targets), 10)}:[/bold cyan] {target}")
            
            try:
                if target.startswith("http") or "." in target:
                    with console.status(f"[cyan]Scanning {target}...[/cyan]"):
                        scanner = WebScanner()
                        asyncio.run(campaign.run_scan(scanner, target))
                    print_success(console, f"Web scan complete: {target}")
                else:
                    with console.status(f"[cyan]Scanning {target}...[/cyan]"):
                        scanner = NetworkScanner()
                        asyncio.run(campaign.run_scan(scanner, target))
                    print_success(console, f"Network scan complete: {target}")
            except Exception as e:
                print_error(console, f"Failed to scan {target}: {str(e)[:100]}")
        
        campaign.complete()
        
        console.print()
        console.print(Panel.fit(
            f"[bold green]Campaign Complete[/bold green]\n"
            f"[cyan]Status:[/cyan] {campaign.status}\n"
            f"[cyan]Results:[/cyan] {len(campaign.results)}",
            border_style="green"
        ))
        
        print_info(console, f"Generate report with: [cyan]nighthawk report {campaign.campaign_id}[/cyan]")
        
    except KeyboardInterrupt:
        print_warning(console, "Assessment cancelled by user")
        raise typer.Exit(130)
    except Exception as exc:
        print_error(console, f"Assessment failed: {exc}")
        raise typer.Exit(1)


@app.command()
def config(
    action: str = typer.Argument("show", help="Action: show, set, reset, export"),
    key: str = typer.Option(None, "--key", "-k", help="Configuration key (e.g., theme.primary_color)"),
    value: str = typer.Option(None, "--value", "-v", help="Configuration value"),
    output: str = typer.Option("config.json", "--output", "-o", help="Output file for export"),
) -> None:
    """Manage user configuration and preferences."""
    from nighthawk.config.user_config import get_config, ConfigManager
    from pathlib import Path
    
    console.print(create_header_panel("Configuration Management", "User Preferences & Settings"))
    console.print()
    
    try:
        config_manager = get_config()
        
        if action == "show":
            # Display current configuration
            config_dict = config_manager.config.model_dump()
            
            def print_config_section(title: str, data: dict, indent: int = 0):
                """Recursively print configuration."""
                prefix = "  " * indent
                if indent == 0:
                    console.print(f"\n[bold cyan]{title}[/bold cyan]")
                    console.print("-" * 60)
                
                for k, v in data.items():
                    if isinstance(v, dict):
                        console.print(f"{prefix}[yellow]{k}:[/yellow]")
                        print_config_section("", v, indent + 1)
                    else:
                        console.print(f"{prefix}[cyan]{k}:[/cyan] [white]{v}[/white]")
            
            console.print(f"[dim]Config file: {config_manager.config_path}[/dim]")
            
            for section in ["theme", "scan", "report"]:
                if section in config_dict:
                    print_config_section(section.upper(), config_dict[section])
            
            # Global settings
            console.print(f"\n[bold cyan]GLOBAL SETTINGS[/bold cyan]")
            console.print("-" * 60)
            for k, v in config_dict.items():
                if k not in ["theme", "scan", "report"]:
                    console.print(f"[cyan]{k}:[/cyan] [white]{v}[/white]")
            
            print_info(console, f"\nEdit config: [cyan]nighthawk config set --key KEY --value VALUE[/cyan]")
            
        elif action == "set":
            if not key or value is None:
                print_error(console, "Both --key and --value are required for 'set' action")
                raise typer.Exit(1)
            
            try:
                # Try to parse value as JSON for complex types
                import json
                try:
                    parsed_value = json.loads(value)
                except json.JSONDecodeError:
                    parsed_value = value
                
                config_manager.set(key, parsed_value)
                config_manager.save_config()
                print_success(console, f"Set {key} = {parsed_value}")
                print_info(console, f"Saved to: {config_manager.config_path}")
            except Exception as e:
                print_error(console, f"Failed to set configuration: {e}")
                raise typer.Exit(1)
        
        elif action == "reset":
            confirm = typer.confirm("Reset all configuration to defaults?")
            if confirm:
                config_manager.reset()
                config_manager.save_config()
                print_success(console, "Configuration reset to defaults")
            else:
                print_info(console, "Reset cancelled")
        
        elif action == "export":
            export_path = Path(output)
            config_manager.export_example(export_path)
            print_success(console, f"Example configuration exported to: {export_path}")
            print_info(console, "Edit this file and place it in ~/.nighthawk/config.json")
        
        else:
            print_error(console, f"Unknown action: {action}")
            print_info(console, "Valid actions: show, set, reset, export")
            raise typer.Exit(1)
    
    except Exception as exc:
        print_error(console, f"Configuration failed: {exc}")
        raise typer.Exit(1)


@app.command()
def report(
    campaign: str = typer.Argument("latest", help="Campaign ID to generate report for (or 'latest')."),
    output: str = typer.Option("report.html", "--output", "-o", help="Output file path."),
    format: str = typer.Option("html", "--format", "-f", help="Report format: html, json, csv."),
) -> None:
    """Generate professional assessment report."""
    from nighthawk.reporting.generator import ReportGenerator
    from nighthawk.models.core import Finding
    import json
    
    console.print(create_header_panel("Report Generation", f"Campaign: {campaign}"))
    console.print()
    
    try:
        print_info(console, f"Generating {format.upper()} report...")
        
        generator = ReportGenerator()
        findings = []  # In production, load from DB for campaign
        
        # Generate based on format
        if format.lower() == "json":
            output = output if output.endswith(".json") else output.replace(".html", ".json")
            generator.generate_json(findings, campaign, output)
            print_success(console, f"JSON report generated: {output}")
        elif format.lower() == "html":
            output = output if output.endswith(".html") else output.replace(".json", ".html")
            generator.generate_html(findings, campaign, output)
            print_success(console, f"HTML report generated: {output}")
        elif format.lower() == "csv":
            output = output if output.endswith(".csv") else output.replace(".html", ".csv")
            # CSV generation would go here
            print_info(console, f"CSV report: {output}")
        else:
            print_error(console, f"Unknown format: {format}")
            raise typer.Exit(1)
        
        # Show report info
        report_path = Path(output)
        if report_path.exists():
            size = report_path.stat().st_size
            print_info(console, f"Report size: {size:,} bytes")
            print_info(console, f"Location: {report_path.absolute()}")
        
        print_success(console, "Report generation complete")
        
    except Exception as exc:
        print_error(console, f"Report generation failed: {exc}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
