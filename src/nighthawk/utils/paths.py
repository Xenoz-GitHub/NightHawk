"""Path utilities for installed package resources."""

from pathlib import Path


def _candidate_roots() -> list[Path]:
    current = Path(__file__).resolve()
    package_dir = current.parent.parent
    project_root = current.parent.parent.parent
    return [
        package_dir,
        project_root,
        *current.parents,
        Path.cwd(),
    ]


def get_package_root() -> Path:
    """Find the project or installed package root that contains bundled data."""
    for candidate in _candidate_roots():
        if not candidate.exists():
            continue
        for possible in (
            candidate,
            candidate / "nighthawk",
            candidate / "src" / "nighthawk",
            candidate / "src",
        ):
            if possible.exists() and any((possible / folder).exists() for folder in ("fingerprints", "rules", "templates", "data")):
                return possible
    return Path(__file__).resolve().parent.parent


def get_fingerprint_dir() -> Path:
    candidates = [
        Path(__file__).resolve().parent.parent / "data" / "fingerprints" / "technologies",
        Path(__file__).resolve().parent.parent / "fingerprints" / "technologies",
        Path(__file__).resolve().parent.parent.parent / "src" / "nighthawk" / "data" / "fingerprints" / "technologies",
        Path(__file__).resolve().parent.parent.parent / "fingerprints" / "technologies",
        get_package_root() / "data" / "fingerprints" / "technologies",
        get_package_root() / "fingerprints" / "technologies",
        get_package_root() / "src" / "nighthawk" / "data" / "fingerprints" / "technologies",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return get_package_root() / "fingerprints" / "technologies"


def get_rules_dir() -> Path:
    candidates = [
        Path(__file__).resolve().parent.parent / "data" / "rules",
        Path(__file__).resolve().parent.parent / "rules",
        Path(__file__).resolve().parent.parent.parent / "src" / "nighthawk" / "data" / "rules",
        Path(__file__).resolve().parent.parent.parent / "rules",
        get_package_root() / "data" / "rules",
        get_package_root() / "rules",
        get_package_root() / "src" / "nighthawk" / "data" / "rules",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return get_package_root() / "rules"


def get_templates_dir() -> Path:
    candidates = [
        Path(__file__).resolve().parent.parent / "data" / "templates",
        Path(__file__).resolve().parent.parent / "templates",
        Path(__file__).resolve().parent.parent.parent / "src" / "nighthawk" / "data" / "templates",
        Path(__file__).resolve().parent.parent.parent / "templates",
        get_package_root() / "data" / "templates",
        get_package_root() / "templates",
        get_package_root() / "src" / "nighthawk" / "data" / "templates",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return get_package_root() / "templates"
