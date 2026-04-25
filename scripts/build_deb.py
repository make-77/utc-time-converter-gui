from __future__ import annotations

import io
import tarfile
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "release" / "linux"
APP_DIR = Path("opt/utc-time-converter")
BIN_PATH = Path("usr/bin/utc-time-converter")
DESKTOP_PATH = Path("usr/share/applications/utc-time-converter.desktop")
CONTROL_PATH = Path("control")
APP_VERSION = "1.1.0"
DEB_NAME = f"utc-time-converter_{APP_VERSION}_all.deb"


def write_ar_member(stream: io.BufferedWriter, name: str, data: bytes, mode: int = 0o100644) -> None:
    header = (
        f"{name}/".ljust(16)
        + f"{int(time.time()):<12}"
        + f"{0:<6}"
        + f"{0:<6}"
        + f"{mode:<8o}"
        + f"{len(data):<10}"
        + "`\n"
    )
    stream.write(header.encode("ascii"))
    stream.write(data)
    if len(data) % 2 == 1:
        stream.write(b"\n")


def add_bytes_tar(tar: tarfile.TarFile, arcname: str, content: bytes, mode: int) -> None:
    info = tarfile.TarInfo(name=arcname)
    info.size = len(content)
    info.mode = mode
    info.mtime = int(time.time())
    tar.addfile(info, io.BytesIO(content))


def build_control_tar() -> bytes:
    control = (
        "Package: utc-time-converter\n"
        f"Version: {APP_VERSION}\n"
        "Section: utils\n"
        "Priority: optional\n"
        "Architecture: all\n"
        "Maintainer: Codex Builder <codex@example.local>\n"
        "Depends: python3, python3-tk, tzdata\n"
        "Description: UTC and timezone conversion desktop GUI\n"
        " A lightweight Tkinter desktop utility for converting UTC, timezones and Unix timestamps.\n"
    ).encode("utf-8")

    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz") as tar:
        add_bytes_tar(tar, str(CONTROL_PATH), control, 0o644)
    return buffer.getvalue()


def build_data_tar() -> bytes:
    launcher = (
        "#!/usr/bin/env sh\n"
        "exec python3 /opt/utc-time-converter/app.py \"$@\"\n"
    ).encode("utf-8")
    desktop = (
        "[Desktop Entry]\n"
        "Type=Application\n"
        "Name=UTC Time Converter\n"
        "Comment=Convert UTC time, IANA timezones and Unix timestamps\n"
        "Exec=utc-time-converter\n"
        "Terminal=false\n"
        "Categories=Utility;\n"
    ).encode("utf-8")

    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz") as tar:
        for file_path in [ROOT / "app.py"]:
            add_bytes_tar(
                tar,
                str(APP_DIR / file_path.name),
                file_path.read_bytes(),
                0o644,
            )
        add_bytes_tar(tar, str(BIN_PATH), launcher, 0o755)
        add_bytes_tar(tar, str(DESKTOP_PATH), desktop, 0o644)
    return buffer.getvalue()


def main() -> None:
    DIST.mkdir(parents=True, exist_ok=True)
    deb_path = DIST / DEB_NAME
    control_tar = build_control_tar()
    data_tar = build_data_tar()

    with deb_path.open("wb") as deb:
        deb.write(b"!<arch>\n")
        write_ar_member(deb, "debian-binary", b"2.0\n", 0o100644)
        write_ar_member(deb, "control.tar.gz", control_tar, 0o100644)
        write_ar_member(deb, "data.tar.gz", data_tar, 0o100644)

    size = deb_path.stat().st_size
    print(f"Built {deb_path} ({size} bytes)")


if __name__ == "__main__":
    main()
