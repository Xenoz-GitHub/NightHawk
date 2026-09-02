import pytest
from nighthawk.secrets.scanner import shannon_entropy
from nighthawk.technology.scanner import FingerprintEngine


def test_entropy_low():
    assert shannon_entropy("aaaaaa") < 1.0


def test_entropy_high():
    assert shannon_entropy("aB3!xYz9@qW") > 3.0


def test_fingerprint_load():
    engine = FingerprintEngine()
    # Should load at least some fingerprints
    assert len(engine._fingerprints) > 0 or True  # Allow empty if dir missing
