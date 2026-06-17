# Agent Rules

- `trash` not rm; `git add <files>` never `.`; Conventional Commits; no emojis
- Session end: keep-test passes → commit → `git push` (ask first)

---

# The tool

Two scripts, ~250 LOC. No package.

| File | Role |
| --- | --- |
| `doc` | docling page-by-page → Markdown; modes: standard, `--vlm`, `--describe`; `--resume`, `--short`, `--out` |
| `minicpm-describe.py` | MiniCPM-V 4.6 figure captioner, own PEP-723 uv env |

## Captioner contract

`minicpm-describe.py <image_dir> [short|normal]` → prints `READY n` / `DONE name`
(drives the progress bar), writes `captions.json`. Model `mlx-community/MiniCPM-V-4.6-4bit`
from `HF_HUB_CACHE` (`~/models`).

## Keep-test (no unit tests by design)

`doc --describe <sample>.pdf` still finds figures and inlines captions. Run it before/after
any change to either script; keep the change only if captions still land.

## Conventions

- `~/.local/bin/doc` → symlink to this repo; edit here.
- `doc` runs under docling's uv-tool python (shebang); `uv tool install docling` provisions it.
- Captioner isolation (mlx-vlm vs docling transformers) is load-bearing — keep the subprocess seam.
