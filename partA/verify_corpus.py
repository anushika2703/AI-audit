from pathlib import Path

CORPUS_DIR = Path(__file__).resolve().parent / "corpus"

LANGUAGES = ["eng", "hin", "tam", "kan"]
EXPECTED_SENTENCES = 997


def verify_file(lang):
    path = CORPUS_DIR / f"{lang}.txt"

    if not path.exists():
        raise FileNotFoundError(f"Missing corpus file: {path}")

    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Remove only newline characters for validation.
    sentences = [line.rstrip("\r\n") for line in lines]

    empty_lines = [i + 1 for i, line in enumerate(sentences) if not line.strip()]

    print(f"{lang}:")
    print(f"  sentences: {len(sentences)}")
    print(f"  empty lines: {len(empty_lines)}")
    print(f"  first sentence: {sentences[0]}")
    print(f"  last sentence: {sentences[-1]}")

    assert len(sentences) == EXPECTED_SENTENCES, (
        f"{lang} has {len(sentences)} sentences, "
        f"expected {EXPECTED_SENTENCES}"
    )

    assert len(empty_lines) == 0, (
        f"{lang} contains empty lines: {empty_lines[:10]}"
    )

    print("  status: PASS\n")


def main():
    print("FLORES-200 corpus verification\n")

    for lang in LANGUAGES:
        verify_file(lang)

    print("All corpus checks passed.")


if __name__ == "__main__":
    main()