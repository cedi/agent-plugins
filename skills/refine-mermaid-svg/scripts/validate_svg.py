#!/usr/bin/env python3
"""Validate editable SVG structure and rendered text containment."""

from __future__ import annotations

import argparse
import csv
import io
import math
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path


INKSCAPE_NS = "http://www.inkscape.org/namespaces/inkscape"
SVG_NS = "http://www.w3.org/2000/svg"
XLINK_NS = "http://www.w3.org/1999/xlink"


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check SVG XML, Inkscape layers, object IDs, and text bounds."
    )
    parser.add_argument("svg", type=Path, help="SVG file to validate")
    parser.add_argument(
        "--require-inkscape",
        action="store_true",
        help="Fail when Inkscape is unavailable",
    )
    parser.add_argument(
        "--require-text-bounds",
        action="store_true",
        help="Measure annotated text against containers using Inkscape",
    )
    parser.add_argument(
        "--min-layers", type=int, default=3, help="Minimum named top-level layers"
    )
    parser.add_argument(
        "--tolerance",
        type=float,
        default=0.75,
        help="Allowed renderer rounding error in SVG user units",
    )
    return parser.parse_args()


def query_geometry(inkscape: str, svg: Path) -> dict[str, tuple[float, float, float, float]]:
    completed = subprocess.run(
        [inkscape, str(svg), "--query-all"],
        check=True,
        text=True,
        capture_output=True,
    )
    geometry: dict[str, tuple[float, float, float, float]] = {}
    for row in csv.reader(io.StringIO(completed.stdout)):
        if len(row) != 5:
            continue
        try:
            geometry[row[0]] = tuple(float(value) for value in row[1:])  # type: ignore[assignment]
        except ValueError:
            continue
    return geometry


def finite_number(value: str | None, fallback: float) -> float:
    if value is None:
        return fallback
    parsed = float(value)
    if not math.isfinite(parsed) or parsed < 0:
        raise ValueError(value)
    return parsed


def main() -> int:
    args = parse_args()
    svg = args.svg.expanduser().resolve()
    errors: list[str] = []
    warnings: list[str] = []

    if not svg.is_file():
        print(f"error: SVG does not exist: {svg}", file=sys.stderr)
        return 2

    try:
        tree = ET.parse(svg)
    except ET.ParseError as exc:
        print(f"error: invalid XML: {exc}", file=sys.stderr)
        return 1

    root = tree.getroot()
    if local_name(root.tag) != "svg":
        errors.append("root element is not <svg>")
    if not root.get("viewBox"):
        errors.append("root <svg> has no viewBox")
    if not root.get("width") or not root.get("height"):
        errors.append("root <svg> must declare width and height")

    elements = list(root.iter())
    ids = [element.get("id") for element in elements if element.get("id")]
    duplicates = sorted(name for name, count in Counter(ids).items() if count > 1)
    if duplicates:
        errors.append(f"duplicate IDs: {', '.join(duplicates)}")

    by_id = {element.get("id"): element for element in elements if element.get("id")}
    forbidden = {"foreignObject", "script", "image", "feDropShadow"}
    present_forbidden = sorted(
        {local_name(element.tag) for element in elements if local_name(element.tag) in forbidden}
    )
    if present_forbidden:
        errors.append(f"forbidden elements: {', '.join(present_forbidden)}")

    direct_layers = [
        child
        for child in root
        if local_name(child.tag) == "g"
        and child.get(f"{{{INKSCAPE_NS}}}groupmode") == "layer"
    ]
    if len(direct_layers) < args.min_layers:
        errors.append(
            f"expected at least {args.min_layers} named top-level Inkscape layers; found {len(direct_layers)}"
        )
    for layer in direct_layers:
        if not layer.get("id"):
            errors.append("top-level Inkscape layer has no id")
        if not layer.get(f"{{{INKSCAPE_NS}}}label"):
            errors.append(f"layer {layer.get('id', '<unknown>')} has no inkscape:label")

    groups = [element for element in elements if local_name(element.tag) == "g"]
    unlabeled_groups = [
        group.get("id")
        for group in groups
        if group.get("id")
        and group.get(f"{{{INKSCAPE_NS}}}groupmode") != "layer"
        and not group.get(f"{{{INKSCAPE_NS}}}label")
    ]
    if unlabeled_groups:
        warnings.append(
            "groups without inkscape:label: " + ", ".join(unlabeled_groups[:12])
            + ("…" if len(unlabeled_groups) > 12 else "")
        )

    texts = [element for element in elements if local_name(element.tag) == "text"]
    bound_texts: list[tuple[ET.Element, str, float, float]] = []
    for text in texts:
        text_id = text.get("id")
        container_id = text.get("data-container")
        free_text = text.get("data-role") == "free-text"
        if not text_id:
            errors.append("a <text> element has no id")
            continue
        if bool(container_id) == free_text:
            errors.append(
                f"text {text_id} must declare exactly one of data-container or data-role=\"free-text\""
            )
            continue
        if not container_id:
            continue
        if container_id not in by_id:
            errors.append(f"text {text_id} references missing container {container_id}")
            continue
        try:
            base_padding = finite_number(text.get("data-padding"), 0.0)
            padding_x = finite_number(text.get("data-padding-x"), base_padding)
            padding_y = finite_number(text.get("data-padding-y"), base_padding)
        except ValueError as exc:
            errors.append(f"text {text_id} has invalid padding value {exc}")
            continue
        bound_texts.append((text, container_id, padding_x, padding_y))

    if not texts:
        warnings.append("SVG contains no text elements")

    inkscape = shutil.which("inkscape")
    if args.require_inkscape and not inkscape:
        errors.append("Inkscape is required but was not found")
    if args.require_text_bounds:
        if not inkscape:
            errors.append("cannot verify text bounds without Inkscape")
        else:
            try:
                geometry = query_geometry(inkscape, svg)
            except subprocess.CalledProcessError as exc:
                errors.append(f"Inkscape geometry query failed with exit code {exc.returncode}")
            else:
                for text, container_id, padding_x, padding_y in bound_texts:
                    text_id = text.get("id", "<unknown>")
                    if text_id not in geometry:
                        errors.append(f"Inkscape returned no geometry for text {text_id}")
                        continue
                    if container_id not in geometry:
                        errors.append(f"Inkscape returned no geometry for container {container_id}")
                        continue
                    tx, ty, tw, th = geometry[text_id]
                    cx, cy, cw, ch = geometry[container_id]
                    tol = args.tolerance
                    left = cx + padding_x
                    top = cy + padding_y
                    right = cx + cw - padding_x
                    bottom = cy + ch - padding_y
                    violations: list[str] = []
                    if tx < left - tol:
                        violations.append(f"left {left - tx:.2f}")
                    if ty < top - tol:
                        violations.append(f"top {top - ty:.2f}")
                    if tx + tw > right + tol:
                        violations.append(f"right {tx + tw - right:.2f}")
                    if ty + th > bottom + tol:
                        violations.append(f"bottom {ty + th - bottom:.2f}")
                    if violations:
                        errors.append(
                            f"text {text_id} exceeds padded bounds of {container_id}: "
                            + ", ".join(violations)
                        )

    xmllint = shutil.which("xmllint")
    if xmllint:
        completed = subprocess.run(
            [xmllint, "--noout", str(svg)], text=True, capture_output=True
        )
        if completed.returncode:
            errors.append("xmllint rejected the SVG")

    for warning in warnings:
        print(f"warning: {warning}")
    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        print(
            f"FAILED: {len(errors)} error(s), {len(warnings)} warning(s) in {svg}",
            file=sys.stderr,
        )
        return 1

    measured = len(bound_texts) if args.require_text_bounds else 0
    print(
        f"PASS: {len(direct_layers)} layers, {len(ids)} IDs, {len(texts)} text objects, "
        f"{measured} measured text bounds"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
