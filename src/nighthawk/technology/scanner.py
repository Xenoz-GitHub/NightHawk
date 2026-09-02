"""Data-driven technology fingerprint engine."""

import yaml
from pathlib import Path
from typing import Any
from collections import defaultdict

from nighthawk.logging.setup import get_logger
from nighthawk.core.exceptions import FingerprintError
from nighthawk.models.core import TechnologyMatch, ConfidenceLevel

logger = get_logger("technology")


from nighthawk.utils.paths import get_fingerprint_dir

class FingerprintEngine:
    """Engine that calculates technology confidence from evidence."""

    def __init__(self, fingerprints_dir: str | Path | None = None) -> None:
        if fingerprints_dir is None:
            fingerprints_dir = get_fingerprint_dir()
        self.fingerprints_dir = Path(fingerprints_dir)
        self._fingerprints: dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        if not self.fingerprints_dir.exists():
            logger.warning("fingerprints_dir_missing", path=str(self.fingerprints_dir))
            return
        for file_path in self.fingerprints_dir.glob("*.yaml"):
            try:
                data = yaml.safe_load(file_path.read_text())
                if data and "name" in data:
                    self._fingerprints[data["name"]] = data
            except Exception as exc:
                logger.warning("fingerprint_load_failed", file=str(file_path), error=str(exc))

    def match_technology(
        self,
        evidence: dict[str, Any],
    ) -> list[TechnologyMatch]:
        """Calculate matches based on collected evidence (headers, HTML, cookies, paths)."""
        results: list[TechnologyMatch] = []
        for name, fp in self._fingerprints.items():
            score = 0.0
            evidences: list[str] = []
            for indicator in fp.get("indicators", []):
                ind_type = indicator.get("type", "")
                weight = indicator.get("weight", 0.5)
                matched = False
                # Header match
                if ind_type == "header":
                    header_name = indicator.get("header", "")
                    pattern = indicator.get("pattern", "")
                    headers = evidence.get("headers", {})
                    for k, v in headers.items():
                        if header_name.lower() == k.lower() and pattern.lower() in v.lower():
                            score += weight
                            evidences.append(f"Header {k} contains '{pattern}'")
                            matched = True
                            break
                # HTML match
                elif ind_type == "html":
                    html_text = evidence.get("html_text", "")
                    pattern = indicator.get("pattern", "")
                    if pattern in html_text:
                        score += weight
                        evidences.append(f"HTML contains '{pattern}'")
                        matched = True
                # Path match
                elif ind_type == "path":
                    paths = evidence.get("paths", [])
                    pattern = indicator.get("pattern", "")
                    for p in paths:
                        if pattern in p:
                            score += weight
                            evidences.append(f"Path contains '{pattern}'")
                            matched = True
                            break
                # Cookie match
                elif ind_type == "cookie":
                    cookies = evidence.get("cookies", [])
                    pattern = indicator.get("pattern", "")
                    for c in cookies:
                        if isinstance(c, dict):
                            name_c = c.get("name", "")
                            if pattern.lower() in name_c.lower():
                                score += weight
                                evidences.append(f"Cookie '{name_c}' matches '{pattern}'")
                                matched = True
                                break
                        elif isinstance(c, str) and pattern.lower() in c.lower():
                            score += weight
                            evidences.append(f"Cookie '{c}' matches '{pattern}'")
                            matched = True
                            break
                # Script match
                elif ind_type == "script":
                    scripts = evidence.get("scripts", [])
                    pattern = indicator.get("pattern", "")
                    for s in scripts:
                        if pattern.lower() in s.lower():
                            score += weight
                            evidences.append(f"Script contains '{pattern}'")
                            matched = True
                            break
                # Cap score at 1.0
                score = min(score, 1.0)

            if score > 0.0:
                level = ConfidenceLevel.CONFIRMED if score >= 0.8 else ConfidenceLevel.LIKELY if score >= 0.5 else ConfidenceLevel.POSSIBLE
                results.append(TechnologyMatch(
                    name=fp.get("name", name),
                    category=fp.get("category", "unknown"),
                    confidence_level=level,
                    evidence=evidences,
                    version=None,
                    version_confidence=0.0,
                ))
        return sorted(results, key=lambda r: r.confidence_level.value if hasattr(r.confidence_level, 'value') else 0, reverse=True)
