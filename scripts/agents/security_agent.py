"""
security_agent.py
Claude Agent #1 - runs after the security scanning stage (OWASP Dependency-Check
+ Trivy filesystem scan). Reads the raw scan output and produces a human-readable
risk-prioritized Markdown report section.
"""
import os
import sys
import glob
from claude_client import call_claude, write_report

SYSTEM_PROMPT = """You are a senior application security engineer reviewing
automated CI/CD security scan output for a Java Spring Boot microservice.
Summarize findings clearly for a development team. For each notable finding,
include: severity, affected component/dependency, risk explanation in plain
language, and a concrete remediation recommendation. End with an overall
risk verdict (LOW / MEDIUM / HIGH / CRITICAL) and whether the pipeline should
proceed to the Docker build stage. Be concise and use Markdown formatting
with headers and tables where useful. If no scan data is available, say so
explicitly rather than inventing findings."""


def read_scan_outputs():
    chunks = []

    # OWASP Dependency-Check report (JSON)
    dep_check_files = glob.glob("target/dependency-check-report/dependency-check-report.json")
    for f in dep_check_files:
        with open(f, "r", encoding="utf-8") as fh:
            content = fh.read()
            chunks.append(f"### OWASP Dependency-Check Report ({f})\n```json\n{content[:8000]}\n```")

    # Trivy filesystem scan report (JSON)
    trivy_files = glob.glob("trivy-fs-report.json")
    for f in trivy_files:
        with open(f, "r", encoding="utf-8") as fh:
            content = fh.read()
            chunks.append(f"### Trivy Filesystem Scan Report ({f})\n```json\n{content[:8000]}\n```")

    if not chunks:
        return "No scan output files were found in the expected locations."
    return "\n\n".join(chunks)


def main():
    scan_data = read_scan_outputs()
    user_prompt = f"""Here is the raw security scan output from this CI run:

{scan_data}

Produce the security stage report section now."""

    report_body = call_claude(SYSTEM_PROMPT, user_prompt)

    final = f"""## 🔒 Stage 2: Security Scanning — Claude Agent Report

**Pipeline run:** {os.environ.get('GITHUB_RUN_ID', 'local')}
**Commit:** {os.environ.get('GITHUB_SHA', 'unknown')[:8]}
**Branch:** {os.environ.get('GITHUB_REF_NAME', 'unknown')}

{report_body}
"""
    write_report("agent-reports/security-report.md", final)


if __name__ == "__main__":
    main()
