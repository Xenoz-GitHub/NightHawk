# NIGHTHAWK — Quick Start

## Install (global CLI)

```bash
pip install git+https://github.com/Xenoz-GitHub/NightHawk.git@v1.0.0
```

Or with `pipx` (recommended):
```bash
pipx install git+https://github.com/Xenoz-GitHub/NightHawk.git@v1.0.0
```

## Verify

```bash
nighthawk --version
nighthawk --help
```

## First scan (auto-creates scope.yaml)

```bash
nighthawk scope --file scope.yaml
nighthawk web https://example.com
```

## Common commands

```bash
nighthawk discover 10.10.10.10
nighthawk tech https://example.com
nighthawk secrets ./repo
nighthawk assess --scope scope.yaml
nighthawk report CAMPAIGN_ID --output report.html
```

No manual setup file creation required — the platform creates a safe default scope automatically.
