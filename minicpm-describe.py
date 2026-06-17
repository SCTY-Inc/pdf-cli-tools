# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "mlx-vlm",
# ]
# ///
"""minicpm-describe — caption every image in a directory with MiniCPM-V 4.6 (MLX).

Runs in its OWN uv environment because mlx-vlm pins a different transformers than
docling. Invoked by the `doc` pipeline (`convert --describe`) as a subprocess so
the two never share a process.

  uv run minicpm-describe.py <image_dir> [short|normal]

Reads HF_HUB_CACHE for the already-downloaded model, captions each image on the
GPU via MLX, writes <image_dir>/captions.json = {filename: caption}. Prints one
line per image so the parent can drive a progress bar:

  READY <n>        once the model is loaded (n = image count)
  DONE  <filename> after each image is captioned
"""
import json
import re
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

_THINK = re.compile(r"<think>.*?</think>", re.DOTALL)

from mlx_vlm import generate, load  # noqa: E402
from mlx_vlm.prompt_utils import apply_chat_template  # noqa: E402
from mlx_vlm.utils import load_config  # noqa: E402

MODEL = "mlx-community/MiniCPM-V-4.6-4bit"
EXTS = {".png", ".jpg", ".jpeg", ".webp"}

# "/no_think" disables MiniCPM-V's chain-of-thought (it otherwise reasons on
# ambiguous images and burns the whole token budget before answering).
_NO_PREAMBLE = " Respond with only the caption text, no preamble. /no_think"
PROMPTS = {
    # terse: one line, ~1.9x faster
    "short": "In one sentence, describe this figure for a document caption, "
    "including any title, key labels, and numbers." + _NO_PREAMBLE,
    # fuller: still grounded, no speculation
    "normal": "Describe this figure for an inline document caption. State what it "
    "shows and transcribe any title, axis labels, legend, and numbers exactly as "
    "written. Describe only what is visible; do not infer conclusions or intent."
    + _NO_PREAMBLE,
}
# budget must cover the (discarded) reasoning block AND the caption that follows
MAX_TOKENS = {"short": 384, "normal": 900}


def _clean(raw: str) -> str:
    """Drop the reasoning trace and any trailing half-finished sentence."""
    text = _THINK.sub("", raw)  # strip closed <think>...</think>
    if "<think>" in text:  # unclosed: budget exhausted mid-reasoning, no caption
        text = text.split("<think>")[0]
    text = " ".join(text.split()).strip()
    # if the model was cut off mid-sentence, keep only complete sentences
    if text and text[-1] not in ".!?\"')":
        cut = max(text.rfind(". "), text.rfind("! "), text.rfind("? "))
        if cut != -1:
            text = text[: cut + 1]
    return text.strip()


def main() -> int:
    d = Path(sys.argv[1])
    length = sys.argv[2] if len(sys.argv) > 2 else "normal"
    if length not in PROMPTS:
        length = "normal"
    imgs = sorted(p for p in d.iterdir() if p.suffix.lower() in EXTS)
    if not imgs:
        (d / "captions.json").write_text("{}")
        return 0

    model, processor = load(MODEL)
    config = load_config(MODEL)
    # disable the model's chain-of-thought: captions, not reasoning traces
    try:
        prompt = apply_chat_template(
            processor, config, PROMPTS[length], num_images=1, enable_thinking=False
        )
    except TypeError:
        prompt = apply_chat_template(processor, config, PROMPTS[length], num_images=1)
    print(f"READY {len(imgs)}", flush=True)

    out = {}
    for p in imgs:
        try:
            res = generate(
                model,
                processor,
                prompt,
                image=[str(p)],
                max_tokens=MAX_TOKENS[length],
                temperature=0.0,
                verbose=False,
            )
            out[p.name] = _clean(res.text) or "(no caption produced)"
        except Exception as e:  # one bad image shouldn't kill the batch
            out[p.name] = f"(description failed: {e})"
        print(f"DONE {p.name}", flush=True)

    (d / "captions.json").write_text(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
