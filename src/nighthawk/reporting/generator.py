"""JSON, HTML, and CSV report generation."""

import json
from datetime import datetime, timezone
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

from nighthawk.logging.setup import get_logger
from nighthawk.models.core import Finding, Severity

logger = get_logger("reporting")


from nighthawk.utils.paths import get_templates_dir

class ReportGenerator:
    """Generate structured reports from campaign results."""

    def __init__(self, templates_dir: str | Path | None = None) -> None:
        if templates_dir is None:
            templates_dir = get_templates_dir()
        self.templates_dir = Path(templates_dir)
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir) if self.templates_dir.exists() else "/"),
            autoescape=select_autoescape(["html", "xml"]),
        )

    def generate_json(self, findings: list[Finding], campaign_id: str, output_path: str) -> None:
        data = {
            "campaign_id": campaign_id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "findings": [f.to_dict_redacted() for f in findings],
        }
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        logger.info("report_json_generated", path=output_path, findings=len(findings))

    def generate_html(self, findings: list[Finding], campaign_id: str, output_path: str) -> None:
        try:
            template = self.env.get_template("report.html")
        except Exception:
            # Fallback inline template
            template_str = """
<!DOCTYPE html>
<html>
<head><title>NIGHTHAWK Report</title></head>
<body>
<h1>NIGHTHAWK Assessment Report</h1>
<p>Campaign: {{ campaign_id }}</p>
<p>Findings: {{ findings_count }}</p>
<table border="1"><tr><th>Title</th><th>Severity</th><th>Category</th></tr>
{% for f in findings %}
<tr><td>{{ f.title }}</td><td>{{ f.severity.value }}</td><td>{{ f.category }}</td></tr>
{% endfor %}
</table>
</body>
</html>
"""
            template = self.env.from_string(template_str)
        content = template.render(
            campaign_id=campaign_id,
            findings=findings,
            findings_count=len(findings),
        )
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info("report_html_generated", path=output_path)
