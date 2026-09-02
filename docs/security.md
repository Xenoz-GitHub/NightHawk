# NIGHTHAWK Security Model

## Scope Enforcement
Every operation validates targets against `scope.yaml`. Unauthorized targets trigger `ScopeViolationError`.

## Redaction
Secrets are never logged or reported in full by default. Redaction uses masking (`sk_live_****9a2f`).

## Input Validation
All file paths are resolved with `pathlib.Path` to prevent directory traversal. Shell execution uses argument arrays, never shell strings.

## Safe Defaults
- No destructive actions are implemented.
- No malware, ransomware, persistence, or covert surveillance features exist.
- Rate limiting, timeouts, and bounded concurrency prevent resource exhaustion.
- Sensitive database URLs use environment variable precedence.

## Auditability
Every assessment records: timestamp, campaign ID, module, target, operation, result, scope decision, and errors. No complete secrets are recorded.

## Platform Boundaries
Windows and Linux collectors perform read-only telemetry. No modifications to services, processes, or system configurations are performed.
