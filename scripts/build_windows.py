"""Build with Windows Python: python scripts/build_windows.py [--desktop]."""

import argparse
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--desktop", action="store_true", help="Also deliver the EXE to the current user's Desktop")
    args = parser.parse_args()
    if sys.platform != "win32":
        parser.error("请使用 Windows Python 打包。")
    root = Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory(prefix="yaoguang-build-") as temporary:
        work = Path(temporary)
        subprocess.run([
            sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean",
            "--onefile", "--windowed", "--uac-admin", "--name", "YaoguangQt",
            "--distpath", str(work / "dist"), "--workpath", str(work / "build"),
            "--specpath", str(work), str(root / "yaoguang_qt.py"),
        ], cwd=root, check=True)
        destination = root / "YaoguangQt.exe"
        shutil.copy2(work / "dist" / "YaoguangQt.exe", destination)
        print(f"Built: {destination}")
    if args.desktop:
        desktop = subprocess.check_output([
            "powershell.exe", "-NoProfile", "-Command",
            "[Console]::OutputEncoding=[System.Text.Encoding]::UTF8; [Environment]::GetFolderPath('Desktop')",
        ], text=True, encoding="utf-8-sig").strip()
        delivered = Path(desktop) / "YaoguangQt.exe"
        shutil.copy2(destination, delivered)
        print(f"Delivered: {delivered}")


if __name__ == "__main__":
    main()
