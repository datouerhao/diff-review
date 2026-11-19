"""Parse ordinary unified text diffs into JSON-compatible dictionaries."""

import re


HUNK_HEADER = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@(.*)$")


def _path(header):
    path = header[4:].split("\t", 1)[0]
    if path.startswith('"'):
        raise ValueError("Git-quoted paths are not supported yet")
    if path == "/dev/null":
        return None
    return path[2:] if path.startswith(("a/", "b/")) else path


def parse_diff(text):
    """Return changed files, hunks and lines with old/new line numbers.

    Supports ordinary unified text diffs with ---/+++ file headers. Binary
    patches, combined merge diffs and Git-quoted paths are not supported.
    Raises ValueError for malformed hunk bodies or unsupported formats.
    """
    files = []
    current = None
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith(("GIT binary patch", "Binary files ", "@@@")):
            raise ValueError("Binary patches and combined diffs are not supported yet")
        if line.startswith("diff --git "):
            current = None
        elif line.startswith("--- "):
            if i + 1 >= len(lines) or not lines[i + 1].startswith("+++ "):
                raise ValueError("Expected +++ file header after ---")
            current = {
                "old_path": _path(line),
                "new_path": _path(lines[i + 1]),
                "hunks": [],
            }
            files.append(current)
            i += 1
        elif line.startswith("@@"):
            match = HUNK_HEADER.fullmatch(line)
            if current is None or match is None:
                raise ValueError("Invalid hunk header or missing file headers")
            old_start, old_count, new_start, new_count, heading = match.groups()
            old_pos, new_pos = int(old_start), int(new_start)
            old_left = int(old_count) if old_count is not None else 1
            new_left = int(new_count) if new_count is not None else 1
            hunk = {
                "old_start": old_pos,
                "old_count": old_left,
                "new_start": new_pos,
                "new_count": new_left,
                "heading": heading.strip(),
                "lines": [],
            }
            current["hunks"].append(hunk)
            i += 1
            while old_left or new_left:
                if i >= len(lines):
                    raise ValueError("Truncated hunk: line counts do not match header")
                body = lines[i]
                if body == "\\ No newline at end of file" and hunk["lines"]:
                    hunk["lines"][-1]["no_newline"] = True
                    i += 1
                    continue
                prefix = body[:1]
                if prefix not in (" ", "+", "-"):
                    raise ValueError("Invalid hunk body: expected context, addition or deletion")
                uses_old = prefix != "+"
                uses_new = prefix != "-"
                if (uses_old and not old_left) or (uses_new and not new_left):
                    raise ValueError("Hunk line counts exceed header")
                hunk["lines"].append({
                    "type": {" ": "context", "+": "add", "-": "delete"}[prefix],
                    "content": body[1:],
                    "old_line": old_pos if uses_old else None,
                    "new_line": new_pos if uses_new else None,
                })
                old_pos += uses_old
                new_pos += uses_new
                old_left -= uses_old
                new_left -= uses_new
                i += 1
            if i < len(lines) and lines[i] == "\\ No newline at end of file":
                if not hunk["lines"]:
                    raise ValueError("No-newline marker without a preceding line")
                hunk["lines"][-1]["no_newline"] = True
                i += 1
            continue
        elif line.startswith(("+", "-", " ", "\\")) and current is not None:
            raise ValueError("Unexpected content outside a hunk")
        i += 1
    if text.strip() and not files:
        raise ValueError("No supported unified text diff found")
    return files
