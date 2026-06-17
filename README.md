# doc

**PDF → Markdown via docling, with a live progress bar and MiniCPM-V 4.6 figure captions.**

Two scripts, ~250 lines. No package, no framework.

- **`doc`** — drives [docling](https://github.com/DS4SD/docling) page-by-page so you get
  a real progress bar (`page 47/232 · ETA 3m`) and crash-resume. Output lands next to the
  source PDF.
- **`minicpm-describe.py`** — captions every figure with **MiniCPM-V 4.6** (MLX, Apple
  Silicon). Runs in its own ephemeral `uv` env because mlx-vlm and docling pin
  incompatible transformers; `doc --describe` invokes it as a subprocess.

## Usage

```bash
doc book.pdf                 # standard pipeline: layout + OCR (Apple Vision if scanned) + tables
doc --vlm book.pdf           # Granite-Docling MLX VLM — one model does layout+OCR+tables
doc --vlm --resume book.pdf  # continue an interrupted run
doc --describe book.pdf      # standard OCR + a MiniCPM-V 4.6 caption of each figure, inline
doc --describe --short book.pdf   # terser captions (~1.9x faster)
doc --out DIR book.pdf       # output directory (default: next to the source PDF)
```

## Setup

```bash
# docling, with the python that doc's shebang points at:
uv tool install docling

# symlink the command (this repo is the source of truth):
ln -s "$PWD/doc" ~/.local/bin/doc
```

`doc --describe` and `--vlm` need Apple Silicon (MLX). MiniCPM-V 4.6 weights download on
first use into `HF_HUB_CACHE` (defaults to `~/models`). The captioner env is resolved
automatically by `uv run` from the PEP-723 header in `minicpm-describe.py` — nothing to install.

## Why MiniCPM-V 4.6

Replaced moondream2 after a head-to-head on real decks: both transcribe chart numbers, but
MiniCPM stays grounded where moondream confabulates a business narrative and misreads a
matrix as a "bar chart". MiniCPM is built for text-bearing images and runs on MLX (no
Ollama, no API).

## Layout

```
doc                   # the CLI (docling page-by-page + resume + describe flow)
minicpm-describe.py   # PEP-723 mlx-vlm figure captioner (isolated env)
```

This repo was once a multi-provider `pdftoolkit` package with a benchmark harness; it
collapsed to the two scripts that are the actual tool. That history is in git
(`git log --follow`).
