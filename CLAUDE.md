# CLAUDE.md

Two scripts, ~250 LOC. PDF → Markdown via docling + MiniCPM-V 4.6 figure captions.
No package, no pyproject, no tests-of-glue — `doc` IS the tool.

## Run

```bash
doc book.pdf [--vlm | --describe] [--short] [--resume] [--out DIR]
```

- standard = heron layout + OCR + TableFormer (page-by-page, resumable)
- `--vlm` = Granite-Docling MLX VLM
- `--describe` = standard OCR + MiniCPM-V 4.6 caption per figure, inline
- `--short` = terser captions, ~1.9x faster (only with `--describe`)

## Files

```
doc                   # CLI: docling page-by-page + resume + describe flow
minicpm-describe.py   # PEP-723 mlx-vlm captioner, own uv env
```

(Was a multi-provider `pdftoolkit` package; collapsed to these two scripts — history in git.)

## Notes

- `trash` not rm
- **Captioner runs in its OWN uv env** — mlx-vlm vs docling transformers conflict. `doc`
  shells out to `minicpm-describe.py` via `uv run` (PEP-723). Located by
  `Path(__file__).resolve().with_name(...)` so it works through the `~/.local/bin/doc` symlink.
- Captioner contract: `minicpm-describe.py <image_dir> [short|normal]` → prints `READY n` /
  `DONE name`, writes `captions.json`. MiniCPM's chain-of-thought is suppressed + stripped.
- Model: `mlx-community/MiniCPM-V-4.6-4bit` from `HF_HUB_CACHE` (`~/models`).
  See `~/models/README.md` for the canonical store + symlink invariant.
- `doc` runs under docling's uv-tool python (shebang). `uv tool install docling` to provision.
- `~/.local/bin/doc` is a symlink to this repo — edit here.
- Apple Silicon required for `--describe` / `--vlm` (MLX). Output: next to source PDF.
- Editing the standalone scripts: no test suite; the keep-test is `doc --describe` on a
  sample PDF still inlining captions.
