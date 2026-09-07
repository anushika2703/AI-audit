from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import fertility
from transformers import AutoTokenizer

CORPUS_DIR = ROOT / "partA" / "corpus"
LANGUAGES = ["eng", "hin", "tam", "kan"]


def analyze(lines, encode):
    total_tokens = 0
    total_words = 0
    total_bytes = 0

    for line in lines:
        tokens = encode(line)
        total_tokens += len(tokens)
        total_words += len(line.split())
        total_bytes += len(line.encode("utf-8"))

    sentences = len(lines)

    return {
        "tokens": total_tokens,
        "sentences": sentences,
        "words": total_words,
        "bytes": total_bytes,
        "tokens_per_sentence": total_tokens / sentences,
        "tokens_per_word": total_tokens / total_words,
        "tokens_per_byte": total_tokens / total_bytes,
    }


def main():
    print("A3.2 — Routing/cost metric comparison\n")

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

    for tokenizer_name, encode in tokenizers.items():

        print(f"=== {tokenizer_name} ===")

        for lang in LANGUAGES:
            path = CORPUS_DIR / f"{lang}.txt"

            with open(path, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]

            result = analyze(lines, encode)

            print(
                f"{lang}: "
                f"tokens/sentence={result['tokens_per_sentence']:.3f}, "
                f"tokens/word={result['tokens_per_word']:.3f}, "
                f"tokens/byte={result['tokens_per_byte']:.3f}"
            )

        print()


if __name__ == "__main__":
    main()