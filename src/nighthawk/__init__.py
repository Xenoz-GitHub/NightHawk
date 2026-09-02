"""NIGHTHAWK — Ethical red-team reconnaissance and attack-surface platform."""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("nighthawk")
except PackageNotFoundError:
    __version__ = "1.0.0-dev"

__author__ = "NIGHTHAWK Development Team"
__license__ = "MIT"
__description__ = "Ethical red-team reconnaissance, attack-surface discovery, and exposure-assessment platform."
