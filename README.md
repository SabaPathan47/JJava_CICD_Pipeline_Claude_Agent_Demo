# Ecommerce API — Spring Boot CI/CD Demo with Claude Agents

A real-world style Spring Boot REST API (product catalog service) with a full
GitHub Actions CI/CD pipeline. Three Claude AI agents are embedded directly
into the pipeline to review and report on key stages.

## Project

- Java 17, Spring Boot 3.3, Spring Data JPA, H2 in-memory DB, Spring Validation
- REST endpoints under `/api/products` (CRUD)
- Unit tests with Spring's MockMvc

Run locally:
```bash
mvn spring-boot:run
```

## Pipeline stages (`.github/workflows/cicd.yml`)

1. **Build & Test** — Maven build, unit tests, JAR uploaded as artifact.
2. **Security Scanning** — OWASP Dependency-Check (SCA) + Trivy filesystem scan
   (secrets, misconfig, vulnerable deps).
   → **Claude Agent #1** (`scripts/agents/security_agent.py`) reads scan
   output and produces a prioritized, plain-English risk report.
3. **Docker Build & Publish** — Multi-stage Dockerfile build, Trivy image
   scan, image pushed to **GitHub Container Registry (GHCR)**.
   → **Claude Agent #2** (`scripts/agents/docker_agent.py`) reviews the
   Dockerfile and image scan results for hygiene/vulnerabilities.
4. **Deploy (simulated)** — No Kubernetes; this stage simulates a deploy
   step (swap in real SSH/`docker run` or cloud deploy commands later).
   → **Claude Agent #3** (`scripts/agents/deploy_agent.py`) summarizes the
   deploy outcome as a release note with a recommended next action.
5. **Comprehensive Report** — Combines all 3 agent reports + build status
   into one Markdown report, published as a workflow artifact and as the
   GitHub Actions job summary.

## Required GitHub setup

1. **Secret:** add `ANTHROPIC_API_KEY` under
   *Repo → Settings → Secrets and variables → Actions → New repository secret*.
2. **GHCR permissions:** no extra setup needed — the workflow uses the
   built-in `GITHUB_TOKEN` with `packages: write` permission to push images
   to `ghcr.io/<owner>/<repo>`.
3. Make sure GHCR package visibility (Settings → Packages) is set as desired
   after the first push (defaults to private).

## Viewing reports

After a workflow run, go to the **Actions** tab → select the run → download
the `final-pipeline-report` artifact, or view the auto-generated **Job
Summary** directly on the run page.
