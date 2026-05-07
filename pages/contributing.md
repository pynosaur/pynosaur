---
layout: default
title: "Contributing"
permalink: /contributing/
---

# Contributing to Pynosaur

Thanks for your interest in contributing to the Pynosaur ecosystem. This guide covers everything from reporting bugs to building entirely new tools.

---

## Quick Links

- [Creating a New Tool](https://github.com/Pynosaur/pynosaur/blob/main/pages/creating-a-program.md) -- full walkthrough from zero to installable CLI
- [Roadmap](/roadmap/) -- planned tools and ecosystem direction
- [Tool Catalog](/) -- existing tools and docs

---

## Ways to Contribute

### Report Bugs

Open an issue in the **tool's own repository** (e.g., [Pynosaur/see](https://github.com/Pynosaur/see/issues) for `see` bugs).

Include:
- What you expected vs. what happened
- Steps to reproduce
- Python version (`python --version`) and OS
- Output of `<tool> --version`

### Suggest Improvements

Have an idea for an existing tool? Open an issue on the tool's repo. For ecosystem-wide suggestions (new conventions, pget features, site improvements), use [Pynosaur/pynosaur](https://github.com/Pynosaur/pynosaur/issues).

### Fix Bugs or Add Features

1. Fork the tool's repository
2. Create a branch (`fix/description` or `feat/description`)
3. Make your changes following the standards below
4. Run tests and blue
5. Open a PR against `main`

### Build a New Tool

See the full [Creating a Program](https://github.com/Pynosaur/pynosaur/blob/main/pages/creating-a-program.md) guide. In short:
1. Check the [Roadmap](https://github.com/Pynosaur/pynosaur/blob/main/ROADMAP.md) for planned tools
2. Open an issue in [Pynosaur/pynosaur](https://github.com/Pynosaur/pynosaur/issues) to discuss
3. Build following the standard layout
4. Submit for inclusion in the ecosystem

### Improve Documentation

- Fix typos, clarify guides, add examples
- PRs to any repo are welcome
- Site content lives in [Pynosaur/pynosaur](https://github.com/Pynosaur/pynosaur) under `pages/` and `docs/`

---

## Code Standards

### Pure Python

All tools use the **Python standard library only**. No pip dependencies. This is the core philosophy -- it keeps tools portable, fast to install, and free from supply-chain risk.

If the stdlib cannot do something, find a creative way or accept the limitation. Do not introduce external packages.

### Style

- **4-space indentation** (enforced by blue)
- **snake_case** for functions and variables
- **Type hints** on function signatures
- **No trailing whitespace** (blue --apply will fix this)
- **Single final newline** at end of files
- **Max line length**: follow blue's configured limit (default 100)

Run `blue .` before committing. The pre-commit hook does this automatically if blue is installed.

### Architecture

- **Thin `main.py`** -- parse arguments, call core logic, print output
- **Logic in `app/core/`** -- pure functions that return data, not print
- **Help from YAML** -- `doc/<name>.yaml` drives `--help` output via `read_app_doc`
- **Tests in `test/`** -- use `unittest` from stdlib

### CLI Conventions

- Always support `-h`/`--help` and `-v`/`--version`
- Exit `0` on success, non-zero on error
- Errors go to stderr, output goes to stdout
- Support `--no-color` for environments without ANSI support
- Follow GNU flag conventions (short `-x`, long `--extended`)

---

## Pull Request Process

### Before Opening a PR

1. **Run tests**: `python test/test_main.py`
2. **Run linter**: `blue .` (zero issues required)
3. **Test manually**: exercise the feature or bugfix by hand
4. **Check cross-platform**: if you touched I/O, networking, or paths, verify on both macOS and Linux if possible

### PR Guidelines

- Keep PRs focused -- one feature or fix per PR
- Write a clear title: `fix: handle empty input in see` or `feat: add --timeout to purl`
- Describe what changed and why in the PR body
- Reference any related issues

### After Merging

When your PR merges to `main` and touches `app/`, `doc/`, or `.program`, the release workflow runs automatically:
1. Reads version from `.program`
2. Creates a GitHub Release tagged `v<version>`

So if your change warrants a new version, **bump the version** in your PR:
- `app/__init__.py`
- `.program`
- `doc/<name>.yaml` VERSION field

All three must match.

---

## Version Bumping

Use semantic-ish versioning:

| Change | Bump | Example |
|--------|------|---------|
| Bug fix | Patch | 0.1.0 -> 0.1.1 |
| New feature (backward-compatible) | Minor | 0.1.1 -> 0.2.0 |
| Breaking change | Major | 0.2.0 -> 1.0.0 |

For tools still at `0.x.y`, minor bumps are fine for new features.

---

## Testing

### Running Tests

```
cd <tool>/
python test/test_main.py
```

### Writing Tests

- Test core logic, not CLI parsing
- Cover edge cases and error paths
- Network tests should handle timeouts gracefully
- Use `color=False` when testing formatted output

### CI Matrix

Tests run on:
- **OS**: ubuntu-latest, macos-latest
- **Python**: 3.8, 3.11, 3.12

Make sure your code works across all of these. Avoid Python 3.9+ features unless the tool explicitly requires it.

---

## Linting with Plack

[Plack](https://github.com/Pynosaur/blue) is the ecosystem's linter. Install it:

```
pget install blue
```

Or run from source:

```
cd /path/to/blue && python app/main.py /path/to/your/tool/
```

Common issues blue catches:
- Indentation not multiple of 4
- Trailing whitespace
- Missing final newline
- Lines too long

Auto-fix with `blue --apply .`

---

## Repository Structure

Each tool is its own repository under the [Pynosaur](https://github.com/Pynosaur) organization:

```
github.com/Pynosaur/<name>/
├── .github/workflows/    # CI + release
├── .githooks/            # pre-commit (blue)
├── app/                  # Source code
│   ├── __init__.py       # __version__
│   ├── main.py           # Entry point
│   ├── core/             # Business logic
│   └── utils/            # doc_reader, helpers
├── doc/<name>.yaml       # Structured docs
├── test/                 # Unit tests
├── .program              # Metadata for pget
├── BUILD                 # Bazel + Nuitka
├── MODULE.bazel          # Bazel config
├── LICENSE               # MIT
└── README.md
```

The meta-repository [Pynosaur/pynosaur](https://github.com/Pynosaur/pynosaur) holds the website, roadmap, and ecosystem docs.

---

## The Ecosystem

### How pget Discovers Tools

`pget search` queries the Pynosaur GitHub org for repositories that contain a `.program` file. That file declares the tool's name, version, and description.

### How pynosaur.org Works

The site is Jekyll, deployed via GitHub Pages. A workflow fetches each tool's README from GitHub and renders it at `pynosaur.org/<name>/`. The sidebar auto-discovers tools from the org.

### How Releases Work

Push to `main` with changes in `app/`, `doc/`, or `.program` triggers `release.yml`, which:
1. Reads version from `.program`
2. Creates (or updates) a GitHub Release with tag `v<version>`

No manual tagging needed.

---

## Getting Help

- Open an issue on [Pynosaur/pynosaur](https://github.com/Pynosaur/pynosaur/issues) for general questions
- Check existing issues and PRs before opening new ones
- Be specific in bug reports -- include version, OS, and reproduction steps

---

## Code of Conduct

Be respectful, constructive, and patient. We are all building this for fun and learning.
