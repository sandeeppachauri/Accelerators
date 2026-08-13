# src/release_notes_agent/cli.py
from __future__ import annotations
import argparse
from .agent import summarize_sync
 
def main() -> None:
    parser = argparse.ArgumentParser(prog="release-notes")
    parser.add_argument("diff_file", help="path to a .diff file")
    args = parser.parse_args()
    with open(args.diff_file) as f:
        print(summarize_sync(f.read()))

if __name__ == "__main__":
    main()
