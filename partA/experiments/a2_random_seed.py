from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import fertility
CORPUS_DIR = ROOT / "partA" / "corpus"

LANGUAGES = ["eng", "hin", "tam", "kan"]


def analyze(lines, encode):
    fertility_values = []
    tpc_values = []

    for line in lines:
        line = line.lower()

        tokens = encode(line)
        words = line.split()

        fertility_values.append(len(tokens) / len(words))
        tpc_values.append(len(tokens) / len(line))

    return (
        sum(fertility_values) / len(fertility_values),
        sum(tpc_values) / len(tpc_values),
    )


def main():
    encode = fertility.load_tokenizer("gpt2")

    print("A2.5 — Random seed impact")
    print()

    for lang in LANGUAGES:
        path = CORPUS_DIR / f"{lang}.txt"
        lines = fertility.read_lines(path)

        # Current benchmark: seed is present
        fertility.random.seed(1337)
        with_seed = analyze(lines, encode)

        # Simulate removing the seed
        fertility.random.seed()
        without_seed = analyze(lines, encode)

        fert_delta = without_seed[0] - with_seed[0]
        tpc_delta = without_seed[1] - with_seed[1]

        print(f"{lang}:")
        print(f"  fertility with seed    : {with_seed[0]:.6f}")
        print(f"  fertility without seed : {without_seed[0]:.6f}")
        print(f"  fertility delta        : {fert_delta:.6f}")
        print(f"  tok/char with seed     : {with_seed[1]:.6f}")
        print(f"  tok/char without seed  : {without_seed[1]:.6f}")
        print(f"  tok/char delta         : {tpc_delta:.6f}")
        print()


if __name__ == "__main__":
    main()