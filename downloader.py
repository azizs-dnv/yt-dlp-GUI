import os
import platform
import subprocess


def open_folder(path: str) -> None:
    """Open folder in OS file manager."""
    if not os.path.isdir(path):
        return

    system = platform.system()
    if system == "Windows":
        os.startfile(path)
    elif system == "Darwin":
        subprocess.call(["open", path])
    else:
        subprocess.call(["xdg-open", path])


def play_bell() -> None:
    """Cross-platform terminal bell."""
    print("\a", end="")


def parse_urls(raw: str):
    return [value.strip() for value in raw.replace(",", "\n").split("\n") if value.strip()]
