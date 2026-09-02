"""ENCRYPTED CREW - NIGHTHAWK — Ethical red-team reconnaissance and attack-surface platform."""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("nighthawk")
except PackageNotFoundError:
    __version__ = "2.0.0-dev"

__author__ = "ENCRYPTED CREW"
__license__ = "MIT"
__description__ = "ENCRYPTED CREW - Ethical red-team reconnaissance, attack-surface discovery, and exposure-assessment platform."
