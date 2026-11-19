# diff-review

An open-source project exploring context-aware code review for Git diffs.

## Status

This project is at the planning stage. The repository currently contains the project outline; the MVP has not been implemented yet. I plan to use Devin to help build the first working version.

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

Implementation, setup instructions, and usage examples will be added as the MVP takes shape.
