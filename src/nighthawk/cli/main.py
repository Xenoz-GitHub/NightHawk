"""NIGHTHAWK CLI main entry point."""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from nighthawk import __version__

console = Console()
app = typer.Typer(
    name="nighthawk",
    help="NIGHTHAWK — Ethical Red-Team Reconnaissance & Attack-Surface Assessment",
    add_completion=False,
    no_args_is_help=True,
)


@app.callback()
def main_callback(
    version: bool = typer.Option(False, "--version", help="Show version and exit."),
) -> None:
    """NIGHTHAWK CLI."""
    if version:
        console.print(f"[bold cyan]NIGHTHAWK[/bold cyan] v{__version__}")
        console.print("Ethical red-team reconnaissance platform.")
        raise typer.Exit()


@app.command()
def scope(
    file: str = typer.Option("scope.yaml", "--file", "-f", help="Scope configuration file."),
) -> None:
    """Validate scope configuration."""
    from nighthawk.scope.manager import ScopeManager
    from nighthawk.core.exceptions import ConfigurationError
    try:
        manager = ScopeManager(file)
        console.print(Panel.fit(f"[green]Scope valid[/green]: {file}", title="Scope Validation"))
        console.print(f"Domains: {manager.config.domains}")
        console.print(f"IPs: {manager.config.ips}")
        console.print(f"CIDRs: {manager.config.cidrs}")
        console.print(f"Authorized modules: {manager.get_authorized_modules()}")
    except ConfigurationError as exc:
        console.print(f"[red]Invalid scope:[/red] {exc}")
        raise typer.Exit(1)


@app.command()
def discover(
    target: str = typer.Argument("...", help="IP, CIDR, or hostname to discover."),
) -> None:
    """Discover authorized network assets."""
    from nighthawk.scope.manager import ScopeManager
    from nighthawk.network.scanner import NetworkScanner
    import asyncio
    try:
        scope = ScopeManager("./scope.yaml")
        scope.validate_target(target)
        scanner = NetworkScanner()
        result = asyncio.run(scanner.run(target, scope_manager=scope))
        table = Table(title=f"Network Scan Results: {target}")
        table.add_column("Port", style="cyan")
        table.add_column("State", style="green")
        table.add_column("Service")
        for r in result.get("results", []):
            table.add_row(str(r.get("port", "")), r.get("state", ""), r.get("service", ""))
        console.print(table)
    except Exception as exc:
        console.print(f"[red]Discover failed:[/red] {exc}")
        raise typer.Exit(1)


@app.command()
def web(
    url: str = typer.Argument("...", help="Target URL or domain."),
) -> None:
    """Assess website security and technology fingerprint."""
    from nighthawk.scope.manager import ScopeManager
    from nighthawk.web.scanner import WebScanner
    import asyncio
    try:
        scope = ScopeManager("./scope.yaml")
        scope.validate_target(url)
        scanner = WebScanner()
        result = asyncio.run(scanner.run(url, scope_manager=scope))
        console.print(Panel.fit(f"Web Assessment: {url}", title="Web Scanner"))
        console.print(f"Status: {result.get('status_code', 'N/A')}")
        console.print(f"Headers: {len(result.get('headers', {}))} observed")
        console.print(f"Security headers analyzed: {len(result.get('security_headers', {}))}")
        console.print(f"TLS supported: {result.get('tls', {}).get('supported', False)}")
        console.print(f"Redirect chain length: {len(result.get('redirect_chain', []))}")
    except Exception as exc:
        console.print(f"[red]Web scan failed:[/red] {exc}")
        raise typer.Exit(1)


@app.command()
def tech(
    url: str = typer.Argument("...", help="Target URL or domain for technology detection."),
) -> None:
    """Detect website technologies."""
    from nighthawk.scope.manager import ScopeManager
    from nighthawk.web.scanner import WebScanner
    from nighthawk.technology.scanner import FingerprintEngine
    import asyncio
    try:
        scope = ScopeManager("./scope.yaml")
        scope.validate_target(url)
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
        table = Table(title=f"Technology Matches: {url}")
        table.add_column("Technology")
        table.add_column("Category")
        table.add_column("Confidence")
        table.add_column("Evidence")
        for m in matches:
            table.add_row(
                m.name,
                m.category,
                m.confidence_level.value,
                ", ".join(m.evidence[:2]),
            )
        console.print(table)
    except Exception as exc:
        console.print(f"[red]Technology detection failed:[/red] {exc}")
        raise typer.Exit(1)


@app.command()
def secrets(
    path: str = typer.Argument(".", help="Path to codebase or repository."),
) -> None:
    """Scan authorized source code for potential secret exposure."""
    from nighthawk.scope.manager import ScopeManager
    from nighthawk.secrets.scanner import SecretScanner
    import asyncio
    try:
        scope = ScopeManager("./scope.yaml")
        scope.validate_target(path)
        scanner = SecretScanner()
        result = asyncio.run(scanner.run(path, scope_manager=scope))
        console.print(Panel.fit(f"Secret Scan: {path}", title="Secret Scanner"))
        findings = result.get("findings", [])
        console.print(f"Findings: {len(findings)}")
        table = Table(title="Potential Secret Findings")
        table.add_column("File")
        table.add_column("Line", justify="right")
        table.add_column("Type")
        table.add_column("Confidence")
        table.add_column("Match (redacted)")
        for f in findings:
            table.add_row(
                str(f.get("file", "")).split("/")[-1],
                str(f.get("line", "")),
                f.get("type", ""),
                f"{f.get('confidence', 0):.2f}",
                f.get("match", ""),
            )
        console.print(table)
    except Exception as exc:
        console.print(f"[red]Secret scan failed:[/red] {exc}")
        raise typer.Exit(1)


@app.command()
def assess(
    scope_file: str = typer.Option("scope.yaml", "--scope", "-s", help="Scope configuration file."),
) -> None:
    """Run a full assessment campaign."""
    from nighthawk.scope.manager import ScopeManager
    from nighthawk.orchestrator.campaign import AssessmentCampaign
    from nighthawk.network.scanner import NetworkScanner
    from nighthawk.web.scanner import WebScanner
    import asyncio
    import uuid
    try:
        scope = ScopeManager(scope_file)
        campaign = AssessmentCampaign(str(uuid.uuid4()), scope)
        console.print(Panel.fit(f"Campaign Started: {campaign.campaign_id}", title="Assessment"))
        # Example: assess all domains
        targets = scope.config.domains or scope.config.ips or ["127.0.0.1"]
        for target in targets[:3]:
            if target.startswith("http") or "." in target:
                scanner = WebScanner()
                asyncio.run(campaign.run_scan(scanner, target))
            else:
                scanner = NetworkScanner()
                asyncio.run(campaign.run_scan(scanner, target))
        campaign.complete()
        console.print(Panel.fit(f"Campaign Complete: {campaign.status}", title="Assessment"))
        console.print(f"Results: {len(campaign.results)}")
    except Exception as exc:
        console.print(f"[red]Assessment failed:[/red] {exc}")
        raise typer.Exit(1)


@app.command()
def report(
    campaign: str = typer.Argument("...", help="Campaign ID to generate report for."),
    output: str = typer.Option("report.html", "--output", "-o", help="Output file path."),
) -> None:
    """Generate assessment report."""
    from nighthawk.reporting.generator import ReportGenerator
    from nighthawk.models.core import Finding
    generator = ReportGenerator()
    findings = []  # In production, load from DB for campaign
    generator.generate_json(findings, campaign, output.replace(".html", ".json"))
    generator.generate_html(findings, campaign, output)
    console.print(f"[green]Report generated:[/green] {output}")


if __name__ == "__main__":
    app()
