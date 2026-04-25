from __future__ import annotations

import shutil
import site
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
APP_FILE = ROOT / "app.py"
RELEASE_DIR = ROOT / "release" / "windows"
ARTIFACTS_DIR = ROOT / ".artifacts" / "pyinstaller"
SPEC = ARTIFACTS_DIR / "utc-time-converter.spec"
BUILD = ARTIFACTS_DIR / "build"
VENDOR_CANDIDATES = [ROOT / "vendor_wheels", ROOT / "vendor_pkgs", ROOT / ".vendor"]


def load_pyinstaller() -> object:
    try:
        import PyInstaller.__main__ as pyinstaller_main  # type: ignore
    except ModuleNotFoundError:
        pyinstaller_main = None
        for vendor_dir in VENDOR_CANDIDATES:
            if not vendor_dir.exists():
                continue
            sys.path.insert(0, str(vendor_dir))
            try:
                import PyInstaller.__main__ as pyinstaller_main  # type: ignore
                break
            except ModuleNotFoundError:
                continue
        if pyinstaller_main is None:
            raise
    return pyinstaller_main


def clean() -> None:
    for path in (BUILD, SPEC):
        if path.is_dir():
            shutil.rmtree(path)
        elif path.exists():
            path.unlink()
    RELEASE_DIR.mkdir(parents=True, exist_ok=True)


def main() -> None:
    site.getusersitepackages = lambda: ""  # type: ignore[assignment]
    sys.path = [path for path in sys.path if "Roaming\\Python" not in path]
    clean()
    pyinstaller_main = load_pyinstaller()
    pyinstaller_main.run(
        [
            "--noconfirm",
            "--clean",
            "--windowed",
            "--onefile",
            "--distpath",
            str(RELEASE_DIR),
            "--workpath",
            str(BUILD),
            "--specpath",
            str(ARTIFACTS_DIR),
            "--name",
            "utc-time-converter",
            str(APP_FILE),
        ]
    )


if __name__ == "__main__":
    main()
