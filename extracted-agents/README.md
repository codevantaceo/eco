# ECO Agents & Automation Bundle

Consolidated, ready-to-migrate agent, bot, automation, and AI components from the repository. Each entry below includes the source path for traceability and retains its original structure for drop-in reuse.

## Contents
- `ai-service/` — `backend/ai`: multi-engine AI microservice (OpenAI-compatible, routing, health, embeddings) with configs and service code.
- `ai-shared-proto/` — `backend/shared/proto`: gRPC/Protobuf contracts and generated Python stubs for the AI service.
- `automation-platform/` — `platforms/automation-platform`: Python automation engine (domain, sandbox, execution and pipeline engines) with tests.
- `platform-shared/` — `platforms/_shared`: shared protocols/utilities required by the automation platform (domain errors, sandbox, protocols).
- `automation-instant/` — `platforms/automation/instant`: TypeScript “instant execution” automation workflows, configs, docs, and scripts.
- `automation-organizer/` — `platforms/automation/organizer`: file/rule/task organizer service that supports the automation stack.
- `superai-platform/` — `platforms/eco-superai/platform-superai`: full AI/quantum multi-agent platform (agents, prompts, embeddings, vector DB, infra, docs, tests).
- `tools/autonomous-bot/` — `tools/autonomous-bot`: autonomous CI/PR bot scripts (detect, fix, branch, merge, PR).
- `tools/ci-issue-repair-engine.py` — `tools/ci-issue-repair-engine.py`: centralized CI failure repair bot.
- `tools/skills/ai-code-editor-workflow-pipeline/` — `tools/skill-creator/skills/ai-code-editor-workflow-pipeline`: skill pack for AI code editing workflows.
- `tools/skills/github-actions-repair-pro/` — `tools/skill-creator/skills/github-actions-repair-pro`: skill pack for GitHub Actions auto-repair.
- `policy/ai_bot_review.rego` — `policy/ai_bot_review.rego`: OPA policy for AI/bot review governance.

## Usage Notes
- Everything is copy-ready inside `extracted-agents/`; no links back to the original tree are required after export.
- Python components expect standard tooling (`pip`, `pytest`) and may rely on the bundled `platform-shared` and `ai-shared-proto` modules. Adjust `PYTHONPATH` to include their `src` directories when running tests.
- Node/TypeScript components (`automation-instant`, `automation-organizer`) keep their package manifests for installation via `npm`/`pnpm`.
- The `superai-platform` bundle includes docs, infra manifests, and scripts alongside the AI agent code for completeness.
- Secrets have been scrubbed and replaced with deployment-time placeholders/env vars; be sure to provide real credentials (e.g., `DATABASE_URL`, `CELERY_BROKER_URL`, `REDIS_URL`) before running.

## Migration Tips
1. Copy or download `extracted-agents/` as a single unit.
2. For Python services, install dependencies from the included `pyproject.toml` files (e.g., `pip install -e ai-service`, `pip install -e automation-platform`).
3. For TypeScript services, install dependencies (`npm install`) from their respective directories before building.
4. Optional: run the included test suites after setting up dependencies to validate the migrated components.
