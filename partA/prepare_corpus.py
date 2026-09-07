from pathlib import Path
import tarfile
import urllib.request
import unicodedata

# FLORES-200 original dataset
URL = "https://dl.fbaipublicfiles.com/nllb/flores200_dataset.tar.gz"

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "raw"
OUT_DIR = ROOT / "corpus"

LANGUAGES = {
    "eng": "eng_Latn",
    "hin": "hin_Deva",
    "tam": "tam_Taml",
    "kan": "kan_Knda",
}


def download_flores():
    DATA_DIR.mkdir(exist_ok=True)

    archive = DATA_DIR / "flores200_dataset.tar.gz"

    if not archive.exists():
        print("Downloading FLORES-200...")
        urllib.request.urlretrieve(URL, archive)
        print("Download complete.")
    else:
        print("FLORES archive already exists.")

    extracted = DATA_DIR / "flores200_dataset"

    if not extracted.exists():
        print("Extracting FLORES-200...")
        with tarfile.open(archive, "r:gz") as tar:
            tar.extractall(DATA_DIR)
        print("Extraction complete.")


def normalize_text(text):
    # Unicode NFC normalization.
    # We do not change words, punctuation, or whitespace.
    return unicodedata.normalize("NFC", text.strip())


def build_corpus():
    dev_dir = DATA_DIR / "flores200_dataset" / "dev"
    OUT_DIR.mkdir(exist_ok=True)

    for short_name, lang_code in LANGUAGES.items():

        source = dev_dir / f"{lang_code}.dev"
        destination = OUT_DIR / f"{short_name}.txt"

        if not source.exists():
            raise FileNotFoundError(f"Missing FLORES file: {source}")

        with open(source, "r", encoding="utf-8") as f:
            sentences = [
                normalize_text(line)
                for line in f
                if line.strip()
            ]

        with open(destination, "w", encoding="utf-8") as f:
            for sentence in sentences:
                f.write(sentence + "\n")

        print(f"{short_name}: {len(sentences)} sentences")


def main():
    download_flores()
    build_corpus()

    print("\nCorpus created successfully.")
    print(f"Output directory: {OUT_DIR}")


if __name__ == "__main__":
    main()