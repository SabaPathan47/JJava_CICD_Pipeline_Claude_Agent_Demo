"""
deploy_agent.py
Claude Agent #3 - runs after the (simulated) deploy stage. Reviews deploy
step logs/outcome and produces a release-readiness summary, plus a rollback
recommendation if the deploy failed.
"""
import os
from claude_client import call_claude, write_report

SYSTEM_PROMPT = """You are a release manager summarizing the outcome of a
deployment step in a CI/CD pipeline for a Java Spring Boot service (deployed
to a simulated/basic target environment, no Kubernetes). Given the deploy log
output and exit status, write a clear release note style summary: what was
deployed, where, the outcome, any warnings worth flagging to the team, and a
recommended next action (e.g. monitor, rollback, manual verification). Keep
it concise and use Markdown."""


def main():
    deploy_log_path = "deploy-log.txt"
    if os.path.exists(deploy_log_path):
        with open(deploy_log_path, "r", encoding="utf-8") as f:
            deploy_log = f.read()[:6000]
    else:
        deploy_log = "No deploy log file found."

    deploy_status = os.environ.get("DEPLOY_STATUS", "unknown")
    environment = os.environ.get("DEPLOY_ENV", "staging (simulated)")
    image_tag = os.environ.get("IMAGE_TAG", "unknown")

    user_prompt = f"""Deploy target environment: {environment}
Image deployed: {image_tag}
Deploy step exit status: {deploy_status}

Deploy log output:
```
{deploy_log}
```

Produce the deploy stage report section now."""

    report_body = call_claude(SYSTEM_PROMPT, user_prompt)

    final = f"""## 🚀 Stage 5: Deploy — Claude Agent Report

**Environment:** {environment}
**Image:** `{image_tag}`
**Status:** {deploy_status}
**Pipeline run:** {os.environ.get('GITHUB_RUN_ID', 'local')}

{report_body}
"""
    write_report("agent-reports/deploy-report.md", final)


if __name__ == "__main__":
    main()
