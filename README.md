# doc

**PDF → Markdown via docling, with a live progress bar and MiniCPM-V 4.6 figure captions.**

Two scripts, ~250 lines. No package, no framework.

| Script | Role |
| --- | --- |
| `doc` | the CLI — drives [docling](https://github.com/DS4SD/docling) page-by-page for a real progress bar (`page 47/232 · ETA 3m`) and crash-resume; writes Markdown next to the source PDF |
| `minicpm-describe.py` | captions every figure with **MiniCPM-V 4.6** (MLX) and hands the text back to `doc` to inline |

## Usage

```bash
doc book.pdf                 # standard pipeline: layout + OCR (Apple Vision if scanned) + tables
doc --vlm book.pdf           # Granite-Docling MLX VLM — one model does layout+OCR+tables
doc --vlm --resume book.pdf  # continue an interrupted run
doc --describe book.pdf      # standard OCR + a MiniCPM-V 4.6 caption of each figure, inline
doc --describe --short book.pdf   # terser captions (~1.9x faster)
doc --out DIR book.pdf       # output directory (default: next to the source PDF)
```

## How it fits together

The two scripts run in **two separate Python environments** — on purpose. mlx-vlm (for
MiniCPM) and docling pin incompatible `transformers` versions, so they can never share a
process. `doc` keeps the captioner at arm's length and shells out to it:

```
  doc                          ← runs in docling's uv-tool env
   │                             (docling + pypdfium2 + rich)
   │  --describe: extract figure crops → temp dir
   ▼
  uv run minicpm-describe.py   ← its OWN ephemeral env (mlx-vlm),
   │                             built on first run from the script's
   │                             PEP-723 header — nothing to pre-install
   │  loads MiniCPM-V-4.6-4bit ──┐
   ▼                            │  weights live in
  captions.json                 └─ HF_HUB_CACHE  (default: ~/models)
   │
   ▼
  inlined into book.md
```

So there are three things on disk:
- **docling's env** — `~/.local/share/uv/tools/docling/` (the python `doc`'s shebang points at)
- **the captioner's env** — ephemeral, managed by `uv run`; you never see or install it
- **the model weights** — `~/models` (`HF_HUB_CACHE`): MiniCPM-V 4.6 + docling's own models

## Setup

You install **one** thing — docling — and symlink the command:

```bash
# 1. docling — provides the python in doc's shebang (#!.../uv/tools/docling/bin/python)
uv tool install docling

# 2. put `doc` on your PATH (this repo is the source of truth)
ln -s "$PWD/doc" ~/.local/bin/doc
```

That's the whole install. The **first** `doc --describe` bootstraps the captioner itself:
`uv run` reads the PEP-723 header in `minicpm-describe.py`, builds a throwaway env with
mlx-vlm, and downloads `mlx-community/MiniCPM-V-4.6-4bit` (~2 GB) into `HF_HUB_CACHE`.
Subsequent runs reuse both.

Requires Apple Silicon (MLX) for `--describe` and `--vlm`. If your uv-tools path differs,
edit the shebang on line 1 of `doc`.

## Why MiniCPM-V 4.6

Replaced moondream2 after a head-to-head on real decks: both transcribe chart numbers, but
MiniCPM stays grounded where moondream confabulates a business narrative and misreads a
matrix as a "bar chart". MiniCPM is built for text-bearing images and runs on MLX — no
Ollama, no API.

---

This repo was once a multi-provider `pdftoolkit` package with a benchmark harness; it
collapsed to the two scripts that are the actual tool. History is in git (`git log --follow`).
