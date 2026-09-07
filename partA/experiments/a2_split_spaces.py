from pathlib import Path
import sys

# Allow importing the original fertility.py from the project root.
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import fertility


CORPUS_DIR = ROOT / "partA" / "corpus"
LANGUAGES = ["eng", "hin", "tam", "kan"]


def analyze_with_split(lines, encode, use_plain_split):
    fertility_values = []
    tpc_values = []

    for line in lines:
        line = line.lower()
        tokens = encode(line)

        if use_plain_split:
            words = line.split()
        else:
            words = line.split(" ")

        chars = len(line)

        fertility_values.append(len(tokens) / len(words))
        tpc_values.append(len(tokens) / chars)

    n = len(fertility_values)

    return (
        sum(fertility_values) / n,
        sum(tpc_values) / n,
    )


def main():
    encode = fertility.load_tokenizer("gpt2")

    print("A2.2 — split(' ') vs split()")
    print()

    for lang in LANGUAGES:
        path = CORPUS_DIR / f"{lang}.txt"
        lines = fertility.read_lines(path)

        original_fert, original_tpc = analyze_with_split(
            lines, encode, use_plain_split=False
        )

        corrected_fert, corrected_tpc = analyze_with_split(
            lines, encode, use_plain_split=True
        )

        fert_delta = corrected_fert - original_fert
        fert_pct = (fert_delta / original_fert) * 100

        tpc_delta = corrected_tpc - original_tpc

        print(f"{lang}:")
        print(f"  original split(' ') fertility : {original_fert:.6f}")
        print(f"  corrected split() fertility   : {corrected_fert:.6f}")
        print(f"  fertility delta                : {fert_delta:.6f}")
        print(f"  fertility delta (%)            : {fert_pct:.4f}%")
        print(f"  tokens/char original           : {original_tpc:.6f}")
        print(f"  tokens/char corrected          : {corrected_tpc:.6f}")
        print(f"  tokens/char delta              : {tpc_delta:.6f}")
        print()


if __name__ == "__main__":
    main()