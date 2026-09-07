from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import fertility
from transformers import AutoTokenizer

CORPUS_DIR = ROOT / "partA" / "corpus"
LANGUAGES = ["eng", "hin", "tam", "kan"]


def count_tokens(lines, encode):
    return sum(len(encode(line)) for line in lines)


def main():
    print("A3.3 — Language token inflation relative to English\n")

    gpt2 = fertility.load_tokenizer("gpt2")

    xlm = AutoTokenizer.from_pretrained(
        "xlm-roberta-base",
        use_fast=True
    )

    tokenizers = {
        "gpt2": gpt2,
        "xlm-roberta-base": lambda text: xlm.encode(
            text,
            add_special_tokens=False
        ),
    }

    corpora = {}

    for lang in LANGUAGES:
        path = CORPUS_DIR / f"{lang}.txt"

        with open(path, "r", encoding="utf-8") as f:
            corpora[lang] = [
                line.strip()
                for line in f
                if line.strip()
            ]

    for tokenizer_name, encode in tokenizers.items():

        token_counts = {}

        for lang in LANGUAGES:
            token_counts[lang] = count_tokens(
                corpora[lang],
                encode
            )

        english_tokens = token_counts["eng"]

        print(f"=== {tokenizer_name} ===")

        for lang in LANGUAGES:
            ratio = token_counts[lang] / english_tokens

            print(
                f"{lang}: "
                f"{token_counts[lang]} tokens, "
                f"{ratio:.3f}x English"
            )

        print()


if __name__ == "__main__":
    main()