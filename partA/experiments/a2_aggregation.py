from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import fertility


CORPUS_DIR = ROOT / "partA" / "corpus"
LANGUAGES = ["eng", "hin", "tam", "kan"]


def analyze(lines, encode):
    # Use whitespace-aware splitting so the previously identified
    # split(" ") issue does not contaminate this experiment.

    line_level_fertility = []

    total_tokens = 0
    total_words = 0

    total_chars = 0

    for line in lines:
        line = line.lower()

        tokens = encode(line)
        words = line.split()
        chars = len(line)

        # Existing methodology:
        line_level_fertility.append(len(tokens) / len(words))

        # Aggregate quantities:
        total_tokens += len(tokens)
        total_words += len(words)
        total_chars += chars

    # Current fertility.py methodology:
    mean_line_fertility = (
        sum(line_level_fertility) / len(line_level_fertility)
    )

    # Alternative corpus-level methodology:
    aggregate_fertility = total_tokens / total_words

    # Same idea for tokens/character.
    mean_line_tpc = sum(
        len(encode(line.lower())) / len(line.lower())
        for line in lines
    ) / len(lines)

    aggregate_tpc = total_tokens / total_chars

    return (
        mean_line_fertility,
        aggregate_fertility,
        mean_line_tpc,
        aggregate_tpc,
        total_tokens,
        total_words,
    )


def main():
    encode = fertility.load_tokenizer("gpt2")

    print("A2.3 — Per-line average vs corpus-level aggregate")
    print()

    for lang in LANGUAGES:
        path = CORPUS_DIR / f"{lang}.txt"
        lines = fertility.read_lines(path)

        (
            line_fertility,
            aggregate_fertility,
            line_tpc,
            aggregate_tpc,
            total_tokens,
            total_words,
        ) = analyze(lines, encode)

        fertility_delta = aggregate_fertility - line_fertility
        fertility_pct = (
            fertility_delta / line_fertility
        ) * 100

        tpc_delta = aggregate_tpc - line_tpc
        tpc_pct = (
            tpc_delta / line_tpc
        ) * 100

        print(f"{lang}:")
        print(f"  sentences                  : {len(lines)}")
        print(f"  total tokens               : {total_tokens}")
        print(f"  total words                : {total_words}")
        print()
        print(f"  current mean tok/word     : {line_fertility:.6f}")
        print(f"  aggregate tok/word        : {aggregate_fertility:.6f}")
        print(f"  fertility delta            : {fertility_delta:.6f}")
        print(f"  fertility delta (%)        : {fertility_pct:.4f}%")
        print()
        print(f"  current mean tok/char     : {line_tpc:.6f}")
        print(f"  aggregate tok/char        : {aggregate_tpc:.6f}")
        print(f"  tok/char delta             : {tpc_delta:.6f}")
        print(f"  tok/char delta (%)         : {tpc_pct:.4f}%")
        print()


if __name__ == "__main__":
    main()