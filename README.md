# diff-review

An open-source project exploring context-aware code review for Git diffs.

## Status

An initial Python prototype parses unified text diffs into structured JSON, including files, hunks, changed lines, and old/new line numbers. Context extraction and automated review are planned and have not been implemented. I plan to use Devin to help develop the broader MVP.

## Planned MVP

- **Git diff parser:** parse changed files, hunks, and added/deleted lines into a structured representation.
- **Tree-sitter context extraction:** connect changed lines to surrounding functions and syntax to provide useful review context.
- **Review output:** produce actionable findings tied to changed files and lines.
- **Reproducible benchmarks:** maintain versioned fixtures and evaluation scripts to measure parsing, context extraction, and review quality.

## Initial milestones

1. Define the diff data model and implement parsing with representative fixtures.
2. Add Tree-sitter context extraction for an initial language.
3. Build an end-to-end command-line prototype.
4. Publish a reproducible benchmark suite and document results and limitations.

## Development

Requires Python 3.9 or later. No third-party dependencies are needed. Run these commands from the repository root:

```sh
# Parse the included example.
python3 -m diff_review examples/hello.diff

# Parse a working-tree diff (ordinary text patches only).
git diff --no-ext-diff --no-color | python3 -m diff_review

# Run the tests.
python3 -m unittest discover -s tests -v
```

The output is a JSON array of files with `old_path`, `new_path`, and `hunks`. Each hunk includes its ranges and lines, with `type` (`context`, `add`, or `delete`), `content`, `old_line`, and `new_line`. A line number is `null` when the line does not exist on that side. New/deleted files use a `null` path for the missing side. No-newline markers set `no_newline` on the preceding line.

This first parser supports ordinary unified text patches with `---`/`+++` headers. It rejects binary patches, combined merge diffs, and Git-quoted paths. Rename-only and mode-only changes are not represented; metadata is ignored in mixed patches, and input containing only metadata returns an error. An empty diff returns `[]`. Malformed hunks return an error and a nonzero CLI exit code.
