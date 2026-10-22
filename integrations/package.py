#!/usr/bin/env python3
"""
Builds the marketplace packages of the CMS plugins into integrations/dist/
(not committed). Each in the shape its marketplace expects -- see
docs/cms-plugins-publishing.md for where each one goes.

    python3 integrations/package.py
"""
import re
import tarfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
SKIP = {".DS_Store", "__pycache__", "tests"}


def files(source: Path, exclude=()):
    for path in sorted(source.rglob("*")):
        rel = path.relative_to(source)
        if path.is_file() and not (set(rel.parts) & SKIP) and rel.as_posix() not in exclude:
            yield path, rel


def version(pattern: str, file: Path) -> str:
    match = re.search(pattern, file.read_text())
    if not match:
        raise SystemExit(f"No version found in {file}")
    return match.group(1)


def zip_dir(source: Path, target: Path, prefix: str = "", exclude=()):
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        for path, rel in files(source, exclude):
            archive.write(path, f"{prefix}{rel.as_posix()}")
    print(f"built {target.relative_to(ROOT)}")


def main():
    wp = ROOT / "wordpress" / "parcella-connector"
    zip_dir(wp, DIST / f"wordpress/parcella-connector-{version(r'Stable tag: ([0-9.]+)', wp / 'readme.txt')}.zip",
            prefix="parcella-connector/")

    joomla = ROOT / "joomla" / "plg_system_parcellaconnector"
    zip_dir(joomla, DIST / f"joomla/plg_system_parcellaconnector-{version(r'<version>([0-9.]+)</version>', joomla / 'parcellaconnector.xml')}.zip")

    typo3 = ROOT / "typo3" / "parcella_connector"
    zip_dir(typo3, DIST / f"typo3/parcella_connector_{version(r'.version. => .([0-9.]+).', typo3 / 'ext_emconf.php')}.zip")

    # drupal.org packages from its own git repository and adds LICENSE.txt
    # itself; this archive is for installing by hand.
    drupal = ROOT / "drupal" / "parcella_connector"
    target = DIST / f"drupal/parcella_connector-{version(r'## ([0-9.]+)', drupal / 'CHANGELOG.md')}.tar.gz"
    target.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(target, "w:gz") as archive:
        for path, rel in files(drupal):
            archive.add(path, f"parcella_connector/{rel.as_posix()}")
    print(f"built {target.relative_to(ROOT)}")

    print("contao: published through Packagist, no archive needed")


if __name__ == "__main__":
    main()
