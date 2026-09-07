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
        # Keep original casing — do not reproduce the lowercasing issue
        tokens = encode(line)
        words = line.split()
        byte_count = len(line.encode("utf-8"))

        total_tokens += len(tokens)
        total_words += len(words)
        total_bytes += byte_count

    return (
        total_tokens,
        total_words,
        total_bytes,
        total_tokens / total_words,
        total_tokens / total_bytes,
    )


def main():
    print("A3.1 — Tokenizer comparison")
    print()

    print("Loading tokenizers...")

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

        print(f"\n=== {tokenizer_name} ===\n")

        for lang in LANGUAGES:
            path = CORPUS_DIR / f"{lang}.txt"
            lines = fertility.read_lines(path)

            (
                total_tokens,
                total_words,
                total_bytes,
                tok_per_word,
                tok_per_byte,
            ) = analyze(lines, encode)

            print(f"{lang}:")
            print(f"  tokens          : {total_tokens}")
            print(f"  words           : {total_words}")
            print(f"  UTF-8 bytes     : {total_bytes}")
            print(f"  tokens/word     : {tok_per_word:.6f}")
            print(f"  tokens/byte     : {tok_per_byte:.6f}")
            print()


if __name__ == "__main__":
    main()