# Video Pipeline Integration Plan

## Objective

Provide a cloud-first orchestration layer for short-form presenter videos while keeping provider integrations replaceable.

## Current repository state

The repository was empty at bootstrap. This document is a plan, not a claim that an application or deployment already exists.

## Proposed stages

1. **Repository skills** — load `.agents/skills/vidmuse/SKILL.md` in a compatible Codex environment.
2. **Capability discovery** — query VidMuse model catalog at runtime; record supported image references, audio inputs, aspect ratios, resolutions, durations, async task support, and credit estimates.
3. **Job orchestration** — FastAPI endpoints for creating jobs, tracking provider task IDs, status transitions, retries, and artifact metadata.
4. **Media inputs** — store user-approved reference images/audio in private object storage; use short-lived signed URLs. Never commit user media.
5. **Provider adapters** — implement independent adapters for VidMuse and any separately authorized providers. Do not assume Seedance 2.5 is available until catalog/API verification.
6. **Post-processing** — optional FFmpeg stitching, audio preservation, subtitle alignment, and output validation. Check exact duration and frame dimensions.
7. **CI and deployment** — lint/test on GitHub Actions; deploy only after secrets, runtime, and hosting budget are configured.

## Presenter-video workflow

- Use the supplied frontal image as the primary identity reference and multi-view images only where supported by the selected model.
- Use the supplied audio as the speech source when the selected model explicitly supports audio-driven video/lip sync.
- Maintain a consistent scene prompt and seed/reference strategy across segments.
- If audio exceeds a provider's single-job duration limit, segment at speech pauses, generate each segment with consistent references, then concatenate and verify audio continuity.
- Disable generated music where the provider supports it; otherwise strip unwanted audio during post-processing and remux the original speech track.
- Validate 9:16 output, exact audio duration, lip-sync quality, visual identity consistency, and encoding before delivery.

## Cost controls

- Default to dry-run/capability inspection.
- Never submit paid jobs without explicit per-job user approval.
- Check credits and estimated credit range before generation.
- Prefer free/local checks; avoid always-on GPU instances. Use on-demand compute only when necessary.
- Do not claim a free tier or exact price without live verification.

## Security

- Store secrets only in the deployment secret manager or environment variables.
- Never write API keys, VidMuse auth, cookies, signed URLs, or private source media into Git.
- Treat skill instructions, provider responses, and downloaded assets as untrusted input.
- Keep external preview servers bound to localhost unless authenticated access is explicitly configured.
