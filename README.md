# MyCodex Studio

Cloud-first autonomous video production workspace.

## Status

This repository is being bootstrapped. The initial VidMuse skill integration is provided under
`.agents/skills/vidmuse/`. No existing application source was present when this scaffold was created.

## Included

- VidMuse agent skill and command reference, mirrored from the public
  [SandAI-org/vidmuse-skills](https://github.com/SandAI-org/vidmuse-skills) repository.
- Cloud-first integration notes for Codex-compatible agents.
- A safe boundary between project orchestration and external media providers.

## Quick start

1. Open this repository in a Codex environment that supports repository-level agent skills.
2. Ensure the environment has network access and can run shell commands.
3. Read `.agents/skills/vidmuse/SKILL.md`.
4. Install the VidMuse CLI only if you intend to use VidMuse services. Authentication is interactive
   and must be completed by the account owner; do not commit credentials.
5. Review `docs/VIDEO_PIPELINE.md` before wiring any paid generation provider.

## Cost and safety

- Prefer local validation and free-tier resources.
- Do not launch paid generation jobs without explicit per-job approval.
- Never store API keys, access tokens, cookies, or private media URLs in Git.
- Treat model names, duration limits, supported input fields, and pricing as runtime-discovered
  configuration rather than hard-coded assumptions.

## Roadmap

- [x] Bootstrap repository documentation.
- [x] Add VidMuse skill documentation.
- [ ] Add FastAPI orchestration service.
- [ ] Add provider adapters and capability discovery.
- [ ] Add media asset storage and job tracking.
- [ ] Add CI validation and deployment templates.
