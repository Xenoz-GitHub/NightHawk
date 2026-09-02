"""Authorized source-code secret scanner."""

import re
import math
from pathlib import Path
from typing import Any
import yaml

from nighthawk.logging.setup import get_logger
from nighthawk.core.exceptions import ScopeViolationError
from nighthawk.models.core import Evidence, Finding, Severity
from nighthawk.scope.manager import ScopeManager
from nighthawk.utils.paths import get_rules_dir

logger = get_logger("secrets")


def shannon_entropy(data: str) -> float:
    """Calculate Shannon entropy of a string."""
    if not data:
        return 0.0
    entropy = 0.0
    length = len(data)
    char_counts: dict[str, int] = {}
    for char in data:
        char_counts[char] = char_counts.get(char, 0) + 1
    for count in char_counts.values():
        p = count / length
        entropy -= p * math.log2(p)
    return entropy


from nighthawk.utils.paths import get_rules_dir

class SecretScanner:
    """Scan authorized repositories for potential secret exposure."""

    def __init__(self, patterns_path: str | Path | None = None) -> None:
        if patterns_path is None:
            patterns_path = get_rules_dir() / "secret_patterns" / "default.yaml"
        self.patterns_path = Path(patterns_path)
        self.patterns: list[dict[str, Any]] = []
        self._load_patterns()
        self.name = "secrets"
        self.version = "1.0.0"

    def _load_patterns(self) -> None:
        if not self.patterns_path.exists():
            logger.warning("secret_patterns_missing", path=str(self.patterns_path))
            return
        try:
            data = yaml.safe_load(self.patterns_path.read_text())
            self.patterns = data.get("patterns", []) if data else []
        except Exception as exc:
            logger.error("secret_patterns_load_failed", error=str(exc))

    async def can_run(self, target: str, scope_config: Any = None) -> bool:
        return Path(target).exists() or target.startswith(("./", "/"))

    async def run(
        self,
        target: str,
        scope_manager: ScopeManager | None = None,
        **context: Any,
    ) -> dict[str, Any]:
        if scope_manager is not None:
            scope_manager.validate_target(target)

        findings: list[dict[str, Any]] = []
        try:
            repo_path = Path(target)
            if not repo_path.exists():
                return {"target": target, "findings": findings, "error": f"Path not found: {target}"}

            file_patterns = ("*.py", "*.ts", "*.js", "*.yaml", "*.yml", "*.json", "*.env", "*.toml", "Dockerfile", "*.sh", "*.md")
            for pattern in file_patterns:
                for file_path in repo_path.rglob(pattern):
                    if file_path.is_file():
                        try:
                            text = file_path.read_text(encoding="utf-8", errors="ignore")
                            findings.extend(await self._scan_file(file_path, text))
                        except Exception as exc:
                            logger.warning("secret_file_read_failed", file=str(file_path), error=str(exc))
        except Exception as exc:
            logger.error("secret_scan_failed", target=target, error=str(exc))
            return {"target": target, "findings": findings, "error": str(exc)}
        return {"target": target, "findings": findings, "count": len(findings)}

    async def _scan_file(self, file_path: Path, text: str) -> list[dict[str, Any]]:
        findings: list[dict[str, Any]] = []
        lines = text.splitlines()
        for line_num, line in enumerate(lines, 1):
            for pattern in self.patterns:
                regex = pattern.get("regex", "")
                severity = pattern.get("severity", "medium")
                context_words = pattern.get("context", [])
                if not regex:
                    continue
                for match in re.finditer(regex, line):
                    matched_text = match.group(0)
                    entropy = shannon_entropy(matched_text)
                    # False positive reduction
                    context_score = 0.0
                    line_lower = line.lower()
                    for word in context_words:
                        if word.lower() in line_lower:
                            context_score += 0.25

                    is_placeholder = any(p in matched_text.lower() for p in ("example", "test", "fake", "dummy", "placeholder", "changeme"))
                    is_high_entropy = entropy > 3.5

                    # Confidence calculation
                    confidence = 0.5 + (context_score * 0.3) + (0.2 if is_high_entropy else 0.0)
                    confidence = max(0.0, min(1.0, confidence))
                    confidence = 0.1 if is_placeholder else confidence

                    if confidence > 0.4 and not is_placeholder:
                        evidence_text = match.group(0)
                        redacted = self._redact_secret(evidence_text)
                        findings.append({
                            "type": pattern.get("name", "unknown"),
                            "file": str(file_path),
                            "line": line_num,
                            "match": redacted,
                            "confidence": round(confidence, 2),
                            "severity": severity,
                            "entropy": round(entropy, 2),
                            "evidence": [
                                f"Matches regex: {regex}",
                                f"Context keywords found: {context_words}",
                                f"Entropy: {entropy:.2f}",
                            ],
                        })
        return findings

    def _redact_secret(self, secret: str) -> str:
        if len(secret) <= 8:
            return "*" * len(secret)
        return secret[:4] + "*" * (len(secret) - 8) + secret[-4:]
