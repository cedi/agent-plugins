---
name: jira-cli
description: Create and manage Jira issues non-interactively using the jira CLI.
  Use when creating epics, tasks, sub-tasks, linking dependencies, or automating
  Jira workflows from the terminal.
---

# Jira CLI for Non-Interactive Automation

Use the `jira` CLI ([ankitpokhrel/jira-cli](https://github.com/ankitpokhrel/jira-cli)) to create and manage Jira issues without interactive prompts. This skill covers the flags, patterns, and gotchas learned from real-world batch operations (creating epics, tasks, and dependency links at scale).

## When to Use This Skill

- Creating Jira epics, tasks, or sub-tasks from the terminal
- Linking issues with dependency relationships (Blocks, etc.)
- Automating bulk Jira operations in scripts or agent workflows
- Editing, viewing, or parsing Jira issue data programmatically

## The Golden Rule

**Always pass `--no-input`** on every create and edit command. Without it, the CLI launches an interactive TUI that fails immediately in non-interactive contexts (pipes, scripts, agents) with an EOF error.

## Commands

### Create an Epic

```bash
jira epic create -pSRE \
  -n "Epic Name" \
  -s "Epic Summary" \
  -yHigh \
  -l label-name \
  --no-input \
  -b$'Description with\nnewlines using $-quoting'
```

| Flag | Purpose | Notes |
|------|---------|-------|
| `-p` | Project key | Required |
| `-n` | Epic name | Required for epics (not used on other types) |
| `-s` | Summary | Required |
| `-y` | Priority | `Low`, `Medium`, `High`, `Very High`, `Blocker` |
| `-l` | Label | Repeatable: `-l alpha -l beta` |
| `-b` | Description body | Use `$'...'` quoting for newlines, or `-b "$(cat body.md)"` for long markdown |
| `--no-input` | Skip interactive prompts | Always include this (on `create`/`edit`; NOT on `link`) |

### Long Markdown Bodies: Write a File, Then `cat` It

For anything longer than a few lines, do NOT fight bash `$'...'` escaping. Write the body
to a `.md` file with your editor tools, then pass it via command substitution:

```bash
jira issue create -pSRE -tBug -P SRE-2128 -yHigh \
  -l intent-slo -l slo-no-data \
  --no-input \
  -s "Short summary line" \
  -b "$(cat /tmp/bug_body.md)"
```

This renders Jira-flavored markdown (headings `###`, tables, fenced code blocks) reliably
and keeps the body under version control / reviewable before filing.

### Required Custom Fields (`--custom key=value`)

Many projects enforce custom fields at creation. Pass each with a repeatable `--custom`
flag using the field's lowercased, hyphenated name (NOT the `customfield_XXXXX` ID):

```bash
jira issue create -pSRE -tBug -P SRE-2177 -yHigh \
  --custom detected-by=Dev --custom bug-severity=Major --custom prod-bug=Yes \
  --no-input -s "..." -b "$(cat body.md)"
```

If a create is rejected for a missing field, the error names the field. Discover allowed
values from an existing issue: `jira issue view SRE-XXXX --raw` and inspect `fields`.

### Capture the New Issue Key from Output

`jira issue create` prints the key/URL to stdout. Capture it for downstream linking:

```bash
out=$(jira issue create -pSRE -tBug -P SRE-2128 --no-input -s "..." -b "$(cat body.md)")
key=$(printf '%s\n' "$out" | grep -oE 'SRE-[0-9]+' | head -n1)
jira issue link "$key" SRE-2359 Blocks   # note: NO --no-input here
```

### Create a Task (Under an Epic)

```bash
jira issue create -pSRE -tTask \
  -P SRE-1234 \
  -s "Task summary" \
  -a "Display Name" \
  -yHigh \
  -l label-name \
  --no-input \
  -b$'Description body'
```

| Flag | Purpose | Notes |
|------|---------|-------|
| `-t` | Issue type | `Task`, `Bug`, `Story`, `Sub-task` |
| `-P` | Parent issue key | Links to parent epic |
| `-a` | Assignee | Use display name, not email |

### Create a Sub-task (Under a Task)

```bash
jira issue create -pSRE -tSub-task \
  -P SRE-5678 \
  -s "Sub-task summary" \
  -a "Display Name" \
  -yMedium \
  --no-input \
  -b$'Description'
```

`-P` is mandatory for sub-tasks. It points to the parent task, not the epic.

### Link Issues (Dependencies)

```bash
jira issue link SRE-1111 SRE-2222 Blocks
```

Format: `jira issue link INWARD OUTWARD LINK_TYPE`

"SRE-1111 Blocks SRE-2222" means SRE-1111 must be done before SRE-2222.

Common link types: `Blocks`, `Duplicate`, `Causes`, `Relates`.

**`jira issue link` does NOT accept `--no-input`** (it is non-interactive already). Passing
it crashes with `unknown flag: --no-input`. Link-type names are also instance-specific —
if a type is rejected, fall back to a safe default like `Relates`:

```bash
jira issue link "$key" SRE-2359 Blocks 2>/dev/null \
  || jira issue link "$key" SRE-2359 Relates
```

### Add a Comment (Body is POSITIONAL)

```bash
jira issue comment add SRE-1234 "Comment body text" --no-input
```

The comment body is a positional argument, not a `-b` flag.

### Edit an Issue

```bash
jira issue edit SRE-1234 -a "Display Name" --no-input
jira issue edit SRE-1234 -s "New summary" -yHigh --no-input
```

Editable fields: `-s` summary, `-b` body, `-y` priority, `-a` assignee, `-l` labels, `-P` parent.

### View an Issue

```bash
jira issue view SRE-1234              # Human-readable
jira issue view SRE-1234 --raw        # JSON output (for parsing)
jira epic list SRE-1234               # List children of an epic
jira epic list SRE-1234 --plain       # Plain text (for scripting)
```

### Parse JSON Output

```bash
jira issue view SRE-1234 --raw | python3 -c "
import sys, json
d = json.load(sys.stdin)
f = d.get('fields', {})
print('Summary:', f.get('summary',''))
print('Status:', f.get('status',{}).get('name',''))
print('Assignee:', f.get('assignee',{}).get('displayName',''))
print('Account ID:', f.get('assignee',{}).get('accountId',''))
for l in f.get('issuelinks', []):
    t = l.get('type',{})
    if 'outwardIssue' in l:
        print(f'{t.get(\"outward\",\"?\")} {l[\"outwardIssue\"][\"key\"]}')
    if 'inwardIssue' in l:
        print(f'{t.get(\"inward\",\"?\")} {l[\"inwardIssue\"][\"key\"]}')
"
```

### Find a User's Display Name

```bash
jira issue view SRE-XXXX --raw | python3 -c "
import sys, json
a = json.load(sys.stdin)['fields']['assignee']
print(f'Name: {a[\"displayName\"]}')
print(f'Email: {a[\"emailAddress\"]}')
print(f'Account ID: {a[\"accountId\"]}')
"
```

Look up an existing issue assigned to the target user, then use the `displayName` value for `-a` flags.

## Gotchas

1. **`--no-input` is non-negotiable.** Without it, create and edit commands launch an interactive TUI that crashes in non-interactive contexts.

2. **`jira issue assign` is always interactive.** It launches a selection menu even when you pass the display name. Use `jira issue edit -a "Name" --no-input` instead, or set `-a` at creation time.

3. **Newlines in descriptions.** Use bash `$'...'` quoting for the `-b` flag: `-b$'Line 1\nLine 2\n\n- Bullet 1\n- Bullet 2'`. Regular single or double quotes do not expand `\n`.

4. **Priority may be required.** Many projects enforce priority. Always pass `-y` to avoid a prompt or rejection.

5. **Assignee uses display name, not email.** Pass the exact display name string (e.g., `"Skyler Mak"`). To discover the correct value, parse `--raw` output from an issue already assigned to that user (see "Find a User's Display Name" above).

6. **Labels are repeatable.** Pass `-l` multiple times: `-l oncall-operator -l documentation`.

7. **Config location.** Default: `~/.config/.jira/.config.yml` (contains `server`, `login`, `project`, `auth_type`). Auth token is stored in the macOS keychain, not in the config file.

8. **`jira issue link` rejects `--no-input`.** It is already non-interactive. Adding the flag fails with `unknown flag: --no-input`. (Only `create`/`edit`/`comment` need `--no-input`.)

9. **Link-type names are instance-specific.** `Blocks` usually works, but if a type is rejected, fall back to `Relates`. Use `jira issue link A B Blocks 2>/dev/null || jira issue link A B Relates`.

10. **A Bug (or Task/Story) cannot be a child of a Sub-task.** `-P` only accepts a parent of a compatible type (e.g. Epic for a Bug/Task; a Task for a Sub-task). To associate a Bug with a Sub-task's work, set `-P <epic>` for the real parent and `jira issue link` the Bug to the Sub-task instead.

11. **Required custom fields use `--custom name=value`, not the field ID.** Use the lowercased hyphenated name (e.g. `--custom detected-by=Dev`), repeatable. A rejected create names the missing field; inspect allowed values via `jira issue view SRE-XXXX --raw`.

12. **`set -e` scripts abort mid-batch on the first bad command.** When filing many issues in one script, a single failed `link` (e.g. the `--no-input` mistake) stops everything after it. Capture each created key to a file as you go so a re-run can resume without duplicating already-created issues.

## Common Workflows

### Create an Epic with Tasks and Dependencies

1. Create the epic, capture the key from stdout.
2. Create tasks with `-P <epic-key>`, capture each task key.
3. Link tasks to each other: `jira issue link TASK-A TASK-B Blocks` for within-epic ordering.
4. Link the new epic to a parent epic: `jira issue link <new-epic> <parent-epic> Blocks`.

### Batch Operations

For creating many issues, chain commands in a single bash call:

```bash
jira issue create -pSRE -tTask -P SRE-100 -s "Task 1" -yHigh --no-input -b$'...' && \
echo "---" && \
jira issue create -pSRE -tTask -P SRE-100 -s "Task 2" -yHigh --no-input -b$'...'
```

For a robust create-then-link batch (file-based bodies, key capture, link fallback,
resume-safe logging), use a helper function:

```bash
file_bug () {  # args: <body.md> <summary> <link-target> <extra-label>
  local out key
  out=$(jira issue create -pSRE -tBug -P SRE-2128 -yHigh \
    -l intent-slo -l "$4" \
    --custom detected-by=Dev --custom bug-severity=Major --custom prod-bug=Yes \
    --no-input -s "$2" -b "$(cat "$1")")
  key=$(printf '%s\n' "$out" | grep -oE 'SRE-[0-9]+' | head -n1)
  jira issue link "$key" "$3" Blocks 2>/dev/null \
    || jira issue link "$key" "$3" Relates
  echo "$key" >> created.txt        # resume-safe log; do NOT re-run created keys
}
```

For bulk linking, use a loop (note: no `--no-input` on `link`):

```bash
for pair in "SRE-101 SRE-102" "SRE-102 SRE-103" "SRE-103 SRE-104"; do
  jira issue link $pair Blocks
done
```

### Dependency Graph Patterns

- **Within-epic:** link tasks that depend on each other for ordering.
- **Cross-epic:** link tasks across epics where real dependencies exist.
- **Epic-level:** link epics to show phase ordering.
- **To parent:** link all new epics to the master/parent epic with Blocks.
