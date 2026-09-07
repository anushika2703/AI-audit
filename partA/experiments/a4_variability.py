from pathlib import Path
import sys
import statistics

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import fertility
from transformers import AutoTokenizer

CORPUS_DIR = ROOT / "partA" / "corpus"
LANGUAGES = ["eng", "hin", "tam", "kan"]


def get_token_counts(lines, encode):
    return [len(encode(line)) for line in lines]


def percentile(values, p):
    values = sorted(values)
    index = int((p / 100) * (len(values) - 1))
    return values[index]


def main():
    print("A4.1 — Token variability\n")

    xlm = AutoTokenizer.from_pretrained(
        "xlm-roberta-base",
        use_fast=True
    )

    encode = lambda text: xlm.encode(
        text,
        add_special_tokens=False
    )

    for lang in LANGUAGES:
        path = CORPUS_DIR / f"{lang}.txt"

        with open(path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]

        counts = get_token_counts(lines, encode)

        print(f"{lang}:")
        print(f"  mean tokens/sentence : {statistics.mean(counts):.3f}")
        print(f"  median               : {statistics.median(counts):.3f}")
        print(f"  p95                  : {percentile(counts, 95):.3f}")
        print(f"  max                  : {max(counts)}")
        print()


if __name__ == "__main__":
    main()