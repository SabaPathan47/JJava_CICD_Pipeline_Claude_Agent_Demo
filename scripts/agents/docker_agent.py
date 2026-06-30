"""
docker_agent.py
Claude Agent #2 - runs after the Docker image build + Trivy image scan stage.
Reviews image scan results and Dockerfile hygiene, producing a report section
on image security, size, and layer/build best practices.
"""
import os
import glob
from claude_client import call_claude, write_report

SYSTEM_PROMPT = """You are a senior DevOps/container security engineer reviewing
a freshly built Docker image for a Java Spring Boot service. You are given:
1) the Dockerfile used to build the image, and
2) a Trivy image vulnerability scan report (JSON).

Summarize: image vulnerability findings (grouped by severity), any Dockerfile
hygiene issues (e.g. running as root, missing multi-stage build, bloated base
image, unpinned versions), and image size considerations if mentioned. End
with an overall verdict (PASS / PASS WITH WARNINGS / FAIL) on whether this
image is safe to publish to the registry and proceed to deploy. Use concise
Markdown with headers and a findings table. If scan data is missing, state
that explicitly."""


def read_dockerfile():
    if os.path.exists("Dockerfile"):
        with open("Dockerfile", "r", encoding="utf-8") as f:
            return f.read()
    return "Dockerfile not found."


def read_image_scan():
    files = glob.glob("trivy-image-report.json")
    if not files:
        return "No Trivy image scan report found."
    with open(files[0], "r", encoding="utf-8") as f:
        return f.read()[:8000]


def main():
    dockerfile = read_dockerfile()
    scan_data = read_image_scan()
    image_tag = os.environ.get("IMAGE_TAG", "unknown")

    user_prompt = f"""Image tag built this run: {image_tag}

Dockerfile used:
```dockerfile
{dockerfile}
```

Trivy image scan report (JSON):
```json
{scan_data}
```

Produce the Docker build stage report section now."""

    report_body = call_claude(SYSTEM_PROMPT, user_prompt)

    final = f"""## 🐳 Stage 4: Docker Build & Image Scan — Claude Agent Report

**Image:** `{image_tag}`
**Pipeline run:** {os.environ.get('GITHUB_RUN_ID', 'local')}
**Commit:** {os.environ.get('GITHUB_SHA', 'unknown')[:8]}

{report_body}
"""
    write_report("agent-reports/docker-report.md", final)


if __name__ == "__main__":
    main()
