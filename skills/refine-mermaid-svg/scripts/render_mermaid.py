#!/usr/bin/env python3
"""Render Mermaid source as a semantic/layout reference SVG."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


PINNED_MERMAID_CLI = "@mermaid-js/mermaid-cli@11.12.0"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render Mermaid to SVG with mmdc or a pinned npx fallback."
    )
    parser.add_argument("input", type=Path, help="Mermaid .mmd input")
    parser.add_argument("output", type=Path, help="Reference .svg output")
    parser.add_argument("--config", type=Path, help="Mermaid JSON configuration")
    parser.add_argument(
        "--background", default="transparent", help="Mermaid background color"
    )
    parser.add_argument(
        "--no-npx",
        action="store_true",
        help="Fail instead of using npx when mmdc is not installed",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source = args.input.expanduser().resolve()
    output = args.output.expanduser().resolve()
    default_config = Path(__file__).resolve().parent.parent / "assets" / "mermaid-config.json"
    config = (args.config or default_config).expanduser().resolve()

    if not source.is_file():
        print(f"error: Mermaid input does not exist: {source}", file=sys.stderr)
        return 2
    if output.suffix.lower() != ".svg":
        print("error: output must use the .svg extension", file=sys.stderr)
        return 2
    if not config.is_file():
        print(f"error: Mermaid config does not exist: {config}", file=sys.stderr)
        return 2

    mmdc = shutil.which("mmdc")
    if mmdc:
        command = [mmdc]
        renderer = mmdc
    elif not args.no_npx and shutil.which("npx"):
        command = ["npx", "--yes", PINNED_MERMAID_CLI]
        renderer = f"npx {PINNED_MERMAID_CLI}"
    else:
        print(
            "error: mmdc is unavailable. Install Mermaid CLI or allow the npx fallback.",
            file=sys.stderr,
        )
        return 2

    output.parent.mkdir(parents=True, exist_ok=True)
    command.extend(
        [
            "--input",
            str(source),
            "--output",
            str(output),
            "--configFile",
            str(config),
            "--backgroundColor",
            args.background,
        ]
    )

    print(f"Rendering reference with {renderer}")
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as exc:
        print(f"error: Mermaid rendering failed with exit code {exc.returncode}", file=sys.stderr)
        return exc.returncode or 1

    print(f"Wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
