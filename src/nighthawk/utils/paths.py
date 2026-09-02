"""Path utilities for installed package resources."""

from pathlib import Path

INSTALLED_ROOT = Path(__file__).resolve().parent.parent.parent


def get_package_root() -> Path:
    """Find package installation root."""
    current = Path(__file__).resolve()
    package_data = INSTALLED_ROOT / "data"
    if package_data.exists():
        return INSTALLED_ROOT
    for parent in [current, *current.parents]:
        if (parent / "src").exists() and (parent / "fingerprints").exists():
            return parent
        if parent.name == "nighthawk" and (parent.parent / "fingerprints").exists():
            return parent.parent
    return INSTALLED_ROOT


def get_fingerprint_dir() -> Path:
    bundled = INSTALLED_ROOT / "data" / "fingerprints" / "technologies"
    if bundled.exists():
        return bundled
    root = get_package_root()
    return root / "fingerprints" / "technologies"


def get_rules_dir() -> Path:
    bundled = INSTALLED_ROOT / "data" / "rules"
    if bundled.exists():
        return bundled
    root = get_package_root()
    return root / "rules"


def get_templates_dir() -> Path:
    bundled = INSTALLED_ROOT / "data" / "templates"
    if bundled.exists():
        return bundled
    root = get_package_root()
    return root / "templates"
