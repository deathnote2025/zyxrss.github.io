#!/usr/bin/env python3

from pathlib import Path
import subprocess
import sys


def main() -> None:
    channel_dir = Path(__file__).resolve().parent
    repo_root = channel_dir.parents[1]
    engine = repo_root / "scripts" / "update_channel.py"
    subprocess.run([sys.executable, str(engine), "--channel-dir", str(channel_dir), *sys.argv[1:]], check=True)


if __name__ == "__main__":
    main()
