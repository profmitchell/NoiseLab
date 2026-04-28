"""Build the installable Procedural Noise Lab add-on zip."""

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = ROOT / "procedural_noise_lab"
OUTPUT = ROOT / "procedural_noise_lab.zip"

EXCLUDED_PARTS = {"__pycache__"}
EXCLUDED_NAMES = {".DS_Store"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}


def should_include(path):
    if any(part in EXCLUDED_PARTS for part in path.parts):
        return False
    if path.name in EXCLUDED_NAMES:
        return False
    if path.suffix in EXCLUDED_SUFFIXES:
        return False
    return path.is_file()


def main():
    with ZipFile(OUTPUT, "w", ZIP_DEFLATED) as archive:
        for path in sorted(PACKAGE_DIR.rglob("*")):
            if should_include(path):
                archive.write(path, path.relative_to(ROOT))
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
