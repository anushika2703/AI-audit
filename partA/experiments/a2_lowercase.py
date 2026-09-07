from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import fertility

CORPUS_DIR = ROOT / "partA" / "corpus"
LANGUAGES = ["eng", "hin", "tam", "kan"]


def analyze(lines, encode, use_lowercase):
    fertility_values = []
    tpc_values = []

    for line in lines:
        if use_lowercase:
            line = line.lower()

        tokens = encode(line)
        words = line.split()

        fertility_values.append(len(tokens) / len(words))
        tpc_values.append(len(tokens) / len(line))

    mean_fertility = sum(fertility_values) / len(fertility_values)
    mean_tpc = sum(tpc_values) / len(tpc_values)

    return mean_fertility, mean_tpc


def main():
    encode = fertility.load_tokenizer("gpt2")

    print("A2.4 — Lowercase vs original text")
    print()

    for lang in LANGUAGES:
        path = CORPUS_DIR / f"{lang}.txt"
        lines = fertility.read_lines(path)

        lowercase_fertility, lowercase_tpc = analyze(
            lines, encode, use_lowercase=True
        )

        original_fertility, original_tpc = analyze(
            lines, encode, use_lowercase=False
        )

        fert_delta = original_fertility - lowercase_fertility
        fert_pct = (fert_delta / lowercase_fertility) * 100

        tpc_delta = original_tpc - lowercase_tpc
        tpc_pct = (tpc_delta / lowercase_tpc) * 100

        print(f"{lang}:")
        print(f"  lowercase fertility : {lowercase_fertility:.6f}")
        print(f"  original fertility  : {original_fertility:.6f}")
        print(f"  fertility delta     : {fert_delta:.6f}")
        print(f"  fertility delta (%) : {fert_pct:.4f}%")
        print()
        print(f"  lowercase tok/char  : {lowercase_tpc:.6f}")
        print(f"  original tok/char   : {original_tpc:.6f}")
        print(f"  tok/char delta      : {tpc_delta:.6f}")
        print(f"  tok/char delta (%)  : {tpc_pct:.4f}%")
        print()


if __name__ == "__main__":
    main()