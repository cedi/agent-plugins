#!/usr/bin/env python3
"""Validate the agent-plugins marketplace.

Dependency-free (Python standard library only) so it needs no side-loaded
packages — just a mise-managed Python, shared by CI and local dev.

Checks performed:
  * marketplace.json: valid JSON, required fields, every entry resolves to a
    plugin dir with a manifest, and the plugin list matches plugins/ on disk.
  * plugin.json: valid JSON, has name + semver version.
  * skills: every plugins/<plugin>/skills/<name>/SKILL.md has valid Agent Skills
    frontmatter (name regex, name == dir, description length).
  * flat skill index: every skills/<name> symlink resolves to its plugin skill.
  * plugin skills are real directories so consumers need not follow symlinks.
  * agents/output-styles: frontmatter has name + description.

Exit code 0 on success, 1 on any error.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+")
KEY_RE = re.compile(r"^([A-Za-z0-9_-]+):(.*)$")

errors: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def load_json(path: Path):
    try:
        return json.loads(path.read_text())
    except Exception as exc:  # noqa: BLE001
        err(f"{path.relative_to(ROOT)}: invalid JSON ({exc})")
        return None


def frontmatter(path: Path) -> dict[str, str] | None:
    """Parse the top-level keys of a SKILL.md/agent YAML frontmatter block.

    Only top-level scalar keys are returned, with multi-line plain/block
    scalars folded to a single space-joined string. That is sufficient for the
    presence/length/name checks below; it deliberately does not implement full
    YAML so the validator stays dependency-free.
    """
    text = path.read_text()
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        err(f"{path.relative_to(ROOT)}: missing YAML frontmatter")
        return None
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        err(f"{path.relative_to(ROOT)}: unterminated frontmatter")
        return None

    data: dict[str, str] = {}
    key: str | None = None
    buf: list[str] = []

    def flush() -> None:
        if key is None:
            return
        val = " ".join(s.strip() for s in buf if s.strip()).strip()
        if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
            val = val[1:-1]
        data[key] = val

    for ln in lines[1:end]:
        m = KEY_RE.match(ln)
        if m and not ln[:1].isspace():
            flush()
            key = m.group(1)
            rest = m.group(2).strip()
            buf = [] if rest in ("|", ">", "|-", ">-", "|+", ">+") or not rest else [rest]
        elif key is not None:
            buf.append(ln)
    flush()
    return data


def check_skill(skill_dir: Path) -> None:
    name = skill_dir.name
    md = skill_dir / "SKILL.md"
    label = skill_dir.relative_to(ROOT)
    if not md.is_file():
        err(f"{label}: missing SKILL.md")
        return
    fm = frontmatter(md)
    if fm is None:
        return
    fm_name = fm.get("name")
    desc = fm.get("description")
    if fm_name != name:
        err(f"{label}: frontmatter name {fm_name!r} != dir {name!r}")
    if not fm_name or not NAME_RE.match(str(fm_name)) or len(str(fm_name)) > 64:
        err(f"{label}: invalid name {fm_name!r}")
    if not desc or not (1 <= len(str(desc)) <= 1024):
        err(f"{label}: description must be 1-1024 chars")


def check_agent_or_style(path: Path) -> None:
    fm = frontmatter(path)
    if fm is None:
        return
    if not fm.get("name"):
        err(f"{path.relative_to(ROOT)}: missing frontmatter name")
    if not fm.get("description"):
        err(f"{path.relative_to(ROOT)}: missing frontmatter description")


def main() -> int:
    skills_root = ROOT / "skills"

    mkt = load_json(ROOT / ".claude-plugin" / "marketplace.json")
    listed: set[str] = set()
    if mkt is not None:
        for field in ("name", "plugins"):
            if field not in mkt:
                err(f"marketplace.json: missing {field!r}")
        for entry in mkt.get("plugins", []):
            for field in ("name", "source", "description"):
                if field not in entry:
                    err(f"marketplace.json: plugin entry missing {field!r}")
            listed.add(entry.get("name", ""))
            src = ROOT / entry.get("source", "")
            if not (src / ".claude-plugin" / "plugin.json").is_file():
                err(f"marketplace.json: {entry.get('name')} source has no plugin.json")

    plugins_root = ROOT / "plugins"
    on_disk = {p.name for p in plugins_root.iterdir() if p.is_dir()}
    for missing in sorted(on_disk - listed):
        err(f"plugins/{missing}: present on disk but not in marketplace.json")
    for extra in sorted(listed - on_disk):
        err(f"marketplace.json: lists {extra!r} with no plugins/ dir")

    plugin_skills: dict[str, Path] = {}
    for plugin in sorted(on_disk):
        pdir = plugins_root / plugin
        manifest = load_json(pdir / ".claude-plugin" / "plugin.json")
        if manifest is not None:
            if not manifest.get("name"):
                err(f"plugins/{plugin}: plugin.json missing name")
            ver = str(manifest.get("version", ""))
            if not SEMVER_RE.match(ver):
                err(f"plugins/{plugin}: plugin.json version {ver!r} not semver")
        sdir = pdir / "skills"
        if sdir.is_dir():
            for skill_dir in sdir.iterdir():
                label = skill_dir.relative_to(ROOT)
                if skill_dir.is_symlink():
                    err(f"{label}: plugin skills must be real directories, not symlinks")
                    continue
                if not skill_dir.is_dir():
                    err(f"{label}: expected a skill directory")
                    continue
                check_skill(skill_dir)
                if skill_dir.name in plugin_skills:
                    other = plugin_skills[skill_dir.name].relative_to(ROOT)
                    err(f"{label}: duplicate skill name, already defined at {other}")
                else:
                    plugin_skills[skill_dir.name] = skill_dir
        for sub in ("agents", "output-styles"):
            d = pdir / sub
            if d.is_dir():
                for md in d.glob("*.md"):
                    check_agent_or_style(md)

    flat_names: set[str] = set()
    for link in skills_root.iterdir():
        flat_names.add(link.name)
        label = link.relative_to(ROOT)
        if not link.is_symlink():
            err(f"{label}: flat skill entries must be symlinks into plugins/")
            continue
        try:
            resolved = link.resolve(strict=True)
        except FileNotFoundError:
            err(f"{label}: broken symlink")
            continue
        expected = plugin_skills.get(link.name)
        if expected is None:
            err(f"{label}: no matching plugin skill")
        elif resolved != expected.resolve():
            target = resolved.relative_to(ROOT) if resolved.is_relative_to(ROOT) else resolved
            err(f"{label}: resolves to {target}, expected {expected.relative_to(ROOT)}")

    for missing in sorted(set(plugin_skills) - flat_names):
        source = plugin_skills[missing].relative_to(ROOT)
        err(f"skills/{missing}: missing flat symlink to {source}")

    if errors:
        print(f"\u2718 {len(errors)} validation error(s):\n")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"\u2714 validation passed: {len(plugin_skills)} skills, {len(on_disk)} plugins")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
