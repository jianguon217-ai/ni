# VidMuse Agent Command Map

This reference is mirrored from SandAI-org/vidmuse-skills at commit f7927f00ba5e9c8453b1ddabfd947aaea0e2c43a.
Upstream: https://github.com/SandAI-org/vidmuse-skills/blob/f7927f00ba5e9c8453b1ddabfd947aaea0e2c43a/skills/vidmuse/references/command-map.md

## Local preview and render

| Task | Command |
|---|---|
| Preview default DSL | `vidmuse serve` |
| Preview a DSL file | `vidmuse serve ./project.dsl.json` |
| Preview on a chosen port | `vidmuse serve ./project.dsl.json --port 5175` |
| Render video | `vidmuse render ./project.dsl.json` |
| Render transparent overlay | `vidmuse render ./project.dsl.json --mode overlay` |

Render requires Node.js 22+ and FFmpeg. Without `HYPERFRAMES_BIN`, first render needs npm network access for pinned HyperFrames.

## Account and catalog

```bash
vidmuse profile get
vidmuse plan get
vidmuse credits get
vidmuse model list
vidmuse model list --video
vidmuse model list --audio
vidmuse model list --image
vidmuse model list --text
```

## Models

```bash
vidmuse model list --search <term>
vidmuse model run --param '{"model_name":"<modelName>","prompt":"<prompt>"}'
vidmuse model run --async --param '{"model_name":"<modelName>","prompt":"<prompt>"}'
vidmuse model result <taskId>
```

Video model examples from upstream show image references via `elements[].reference_image_urls` or `elements[].frontal_image_url`, reference video via `elements[].video_url`, and audio via `audios[].url`. Exact fields must be checked against the discovered model's contract; the CLI does not infer or remap prompt fields.

## Assets, styles and voices

```bash
vidmuse asset list
vidmuse asset list --video --uploaded
vidmuse style list
vidmuse style list --scope all
vidmuse voice list
vidmuse voice search -q "calm narration"
```

## Threads and messages

```bash
vidmuse thread create --text "Create a video"
vidmuse thread list --limit 20
vidmuse thread status <threadId>
vidmuse message list --thread <threadId> --last 5
vidmuse message send --thread <threadId> --text "Revise the video"
```

Thread/message writes and media generation mutate account state or may consume credits; obtain user intent and check cost first.

## Authentication

```bash
vidmuse login
vidmuse login --device
vidmuse login --device --start
vidmuse login --device --complete
vidmuse logout
```

Ask before initiating login; it requires user action.
