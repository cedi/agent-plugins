#!/usr/bin/env python3
"""Render an SVG preview through Inkscape."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export a PNG preview with Inkscape.")
    parser.add_argument("input", type=Path, help="Input SVG")
    parser.add_argument("output", type=Path, help="Output PNG")
    parser.add_argument("--width", type=int, help="Export width in pixels")
    parser.add_argument("--height", type=int, help="Export height in pixels")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source = args.input.expanduser().resolve()
    output = args.output.expanduser().resolve()
    inkscape = shutil.which("inkscape")

    if not source.is_file():
        print(f"error: SVG input does not exist: {source}", file=sys.stderr)
        return 2
    if output.suffix.lower() != ".png":
        print("error: output must use the .png extension", file=sys.stderr)
        return 2
    if not inkscape:
        print("error: Inkscape is required for preview rendering", file=sys.stderr)
        return 2

    output.parent.mkdir(parents=True, exist_ok=True)
    command = [
        inkscape,
        str(source),
        "--export-type=png",
        f"--export-filename={output}",
        "--export-area-page",
    ]
    if args.width:
        command.append(f"--export-width={args.width}")
    if args.height:
        command.append(f"--export-height={args.height}")

    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as exc:
        print(f"error: Inkscape export failed with exit code {exc.returncode}", file=sys.stderr)
        return exc.returncode or 1

    print(f"Wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
