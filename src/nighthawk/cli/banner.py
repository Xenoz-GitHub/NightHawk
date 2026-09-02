"""ENCRYPTED CREW - Professional ASCII banner and branding."""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
import sys
import os

# Set console encoding to UTF-8 for Windows
if sys.platform == "win32":
    try:
        # Try to set UTF-8 encoding for Windows
        os.system("chcp 65001 > nul 2>&1")
    except:
        pass

# ENCRYPTED CREW ASCII Art Banner (Windows-compatible)
ENCRYPTED_CREW_BANNER = r"""
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
"""

# Fallback ASCII banner for systems that don't support box drawing characters
ENCRYPTED_CREW_BANNER_SIMPLE = r"""
  _____ _   _  ____ ______   ______ _____ ______ _____  
 |  ___| \ | |/ ___|  _ \ \ / /  _ \_   _|  ____|  __ \ 
 | |__ |  \| | |   | |_) \ V /| |_) || | | |__  | |  | |
 |  __|| . ` | |   |  _ < \ / |  __/ | | |  __| | |  | |
 | |___| |\  | |___| |_) | | | |    | | | |____| |__| |
 |_____|_| \_|\____|____/  |_|_|    |_| |______|_____/ 
                                                        
   ____ ____  _______        __
  / ___|  _ \| ____\ \      / /
 | |   | |_) |  _|  \ \ /\ / / 
 | |___|  _ <| |___  \ V  V /  
  \____|_| \_\_____|  \_/\_/   
"""

NIGHTHAWK_SMALL = r"""
  ╔╗╔╦╔═╗╦ ╦╔╦╗╦ ╦╔═╗╦ ╦╦╔═
  ║║║║║ ╦╠═╣ ║ ╠═╣╠═╣║║║╠╩╗
  ╝╚╝╩╚═╝╩ ╩ ╩ ╩ ╩╩ ╩╚╩╝╩ ╩
"""

NIGHTHAWK_SMALL_SIMPLE = r"""
  _  _ ___ ___ _  _ _____ _  _   ___      _____ 
 | \| |_ _/ __| || |_   _| || | /_\ \    / / _ \
 | .` || | (_ | __ | | | | __ |/ _ \ \/\/ /|   /
 |_|\_|___\___|_||_| |_| |_||_/_/ \_\_/\_/ |_|_\
"""


def can_use_unicode() -> bool:
    """Check if the console supports unicode characters."""
    try:
        # Try to encode a box-drawing character
        test_char = "╔"
        if sys.platform == "win32":
            # On Windows, check if we can encode to the console encoding
            test_char.encode(sys.stdout.encoding or 'utf-8')
        else:
            test_char.encode('utf-8')
        return True
    except (UnicodeEncodeError, AttributeError):
        return False


def print_banner(console: Console, version: str = "1.0.0") -> None:
    """Print the ENCRYPTED CREW banner with styling."""
    use_unicode = can_use_unicode()
    
    # Choose appropriate banner
    banner_text = Text(ENCRYPTED_CREW_BANNER if use_unicode else ENCRYPTED_CREW_BANNER_SIMPLE)
    banner_text.stylize("bold cyan")
    
    try:
        console.print(banner_text)
    except UnicodeEncodeError:
        # Fallback to simple banner
        banner_text = Text(ENCRYPTED_CREW_BANNER_SIMPLE)
        banner_text.stylize("bold cyan")
        console.print(banner_text)
    
    # Tagline with red accent
    tagline = Text()
    tagline.append("=" * 80, style="dim white")
    tagline.append("\n")
    tagline.append("  [*] ", style="bold red")
    tagline.append("NIGHTHAWK ", style="bold cyan")
    tagline.append("v" + version, style="bold green")
    tagline.append(" | ", style="dim white")
    tagline.append("Ethical Red-Team Reconnaissance Platform", style="bold white")
    tagline.append("\n")
    tagline.append("  ", style="dim white")
    tagline.append(">>> ", style="bold yellow")
    tagline.append("Attack Surface Discovery", style="green")
    tagline.append(" | ", style="dim white")
    tagline.append("Security Assessment", style="green")
    tagline.append(" | ", style="dim white")
    tagline.append("Threat Intelligence", style="green")
    tagline.append("\n")
    tagline.append("=" * 80, style="dim white")
    
    console.print(tagline)
    console.print()


def print_small_banner(console: Console) -> None:
    """Print a smaller banner for command output."""
    use_unicode = can_use_unicode()
    text = Text(NIGHTHAWK_SMALL if use_unicode else NIGHTHAWK_SMALL_SIMPLE)
    text.stylize("bold cyan")
    try:
        console.print(text)
    except UnicodeEncodeError:
        text = Text(NIGHTHAWK_SMALL_SIMPLE)
        text.stylize("bold cyan")
        console.print(text)


def print_success(console: Console, message: str) -> None:
    """Print success message with styling."""
    console.print(f"[bold green][+][/bold green] {message}")


def print_error(console: Console, message: str) -> None:
    """Print error message with styling."""
    console.print(f"[bold red][-][/bold red] {message}")


def print_warning(console: Console, message: str) -> None:
    """Print warning message with styling."""
    console.print(f"[bold yellow][!][/bold yellow] {message}")


def print_info(console: Console, message: str) -> None:
    """Print info message with styling."""
    console.print(f"[bold cyan][i][/bold cyan] {message}")


def create_header_panel(title: str, subtitle: str = "") -> Panel:
    """Create a styled header panel for commands."""
    text = Text()
    text.append(">>> ", style="bold cyan")
    text.append(title, style="bold white")
    text.append(" <<<", style="bold cyan")
    if subtitle:
        text.append("\n")
        text.append(subtitle, style="dim white")
    
    return Panel.fit(
        text,
        border_style="cyan",
        padding=(0, 2),
    )


def create_status_text(status: str, message: str) -> Text:
    """Create styled status text."""
    text = Text()
    
    if status.lower() == "success":
        text.append("[+] ", style="bold green")
        text.append(message, style="green")
    elif status.lower() == "error":
        text.append("[-] ", style="bold red")
        text.append(message, style="red")
    elif status.lower() == "warning":
        text.append("[!] ", style="bold yellow")
        text.append(message, style="yellow")
    elif status.lower() == "info":
        text.append("[i] ", style="bold cyan")
        text.append(message, style="cyan")
    else:
        text.append(message, style="white")
    
    return text
