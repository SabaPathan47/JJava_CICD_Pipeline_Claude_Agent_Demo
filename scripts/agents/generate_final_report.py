"""
generate_final_report.py
Combines the outputs of all 3 Claude agents (security, docker, deploy) plus
the build stage status into a single comprehensive pipeline report, written
as agent-reports/FINAL_PIPELINE_REPORT.md and also used as the GitHub Actions
job summary.
"""
import os
from datetime import datetime, timezone

REPORT_DIR = "agent-reports"


def read_or_placeholder(path: str, label: str) -> str:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return f"## {label}\n\n_Report not available for this run (stage may have been skipped or failed before the agent ran)._\n"


def main():
    build_status = os.environ.get("BUILD_STATUS", "unknown")
    repo = os.environ.get("GITHUB_REPOSITORY", "unknown/repo")
    run_id = os.environ.get("GITHUB_RUN_ID", "local")
    run_url = f"https://github.com/{repo}/actions/runs/{run_id}" if repo != "unknown/repo" else "N/A"
    branch = os.environ.get("GITHUB_REF_NAME", "unknown")
    commit = os.environ.get("GITHUB_SHA", "unknown")[:8]
    actor = os.environ.get("GITHUB_ACTOR", "unknown")
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    security_section = read_or_placeholder(f"{REPORT_DIR}/security-report.md", "Stage 2: Security Scanning")
    docker_section = read_or_placeholder(f"{REPORT_DIR}/docker-report.md", "Stage 4: Docker Build & Image Scan")
    deploy_section = read_or_placeholder(f"{REPORT_DIR}/deploy-report.md", "Stage 5: Deploy")

    final_report = f"""# 📋 CI/CD Pipeline — Comprehensive Report

**Repository:** {repo}
**Branch:** {branch}
**Commit:** `{commit}`
**Triggered by:** {actor}
**Generated:** {timestamp}
**Workflow run:** {run_url}

---

## 🔨 Stage 1: Build & Test

**Status:** {build_status}

Maven build and unit test execution for the `ecommerce-api` Spring Boot service.

---

{security_section}

---

{docker_section}

---

{deploy_section}

---

## ✅ Summary

This report was assembled automatically from three independent Claude agent
reviews run at the Security Scanning, Docker Build, and Deploy stages of the
pipeline, combined with the Build stage status. Review each section above for
stage-specific findings and recommended actions before promoting this build
further.
"""

    os.makedirs(REPORT_DIR, exist_ok=True)
    with open(f"{REPORT_DIR}/FINAL_PIPELINE_REPORT.md", "w", encoding="utf-8") as f:
        f.write(final_report)

    # Also write to GitHub Actions job summary if available
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as f:
            f.write(final_report)

    print(f"Final comprehensive report written to {REPORT_DIR}/FINAL_PIPELINE_REPORT.md")


if __name__ == "__main__":
    main()
