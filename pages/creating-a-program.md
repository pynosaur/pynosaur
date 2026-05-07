---
layout: default
title: "Creating a Program"
permalink: /creating-a-program/
published: false
---

# Creating a Pynosaur Program

This guide walks you through building a new tool for the Pynosaur ecosystem — from an empty directory to a fully installable, testable, and deployable CLI program.

---

## Overview

Every Pynosaur tool follows the same conventions. By sticking to this structure, your tool will:

- Be **discoverable** by `pget search`
- Be **installable** via `pget install <name>`
- Appear **automatically** in the [pynosaur.org](https://pynosaur.org) sidebar
- Run through **CI/CD** with linting, testing, and releases
- Build into a **standalone binary** via Bazel + Nuitka

---

## 1. Choose a Name

Pick a short, memorable name that:

- Does **not** conflict with existing Unix commands (avoid `ls`, `cat`, `grep`, etc.)
- Suggests what the tool does (e.g., `see` for viewing files, `sock` for sockets)
- Is lowercase, no hyphens or underscores

Check existing tools at [pynosaur.org](https://pynosaur.org) to avoid collisions.

---

## 2. Directory Structure

Every Pynosaur tool follows this exact layout:

```
<name>/
├── .github/
│   └── workflows/
│       ├── test.yml          # CI: lint + test + optional build
│       └── release.yml       # Auto-release on version bump
├── .githooks/
│   └── pre-commit            # Local blue lint hook
├── app/
│   ├── __init__.py           # __version__ = "0.1.0"
│   ├── main.py               # CLI entry point
│   ├── core/
│   │   ├── __init__.py
│   │   └── <logic>.py        # Core business logic
│   └── utils/
│       ├── __init__.py
│       └── doc_reader.py     # YAML documentation reader
├── doc/
│   └── <name>.yaml           # Structured documentation
├── test/
│   ├── __init__.py
│   └── test_main.py          # Unit tests
├── .gitignore
├── .program                  # Program metadata (required for pget)
├── BUILD                     # Bazel genrule for Nuitka binary
├── LICENSE                   # MIT License
├── MODULE.bazel              # Bazel module configuration
└── README.md                 # Project documentation
```

---

## 3. The `.program` File

This is the **most important file**. Without it, `pget` will not recognize your tool as installable.

```yaml
name: <name>
version: 0.1.0
author: <your-github-handle>
description: One-line description of your tool
type: cli-tool
```

The `version` field is used by the release workflow to create GitHub tags (`v0.1.0`). Bump it when you release.

---

## 4. The Entry Point — `app/main.py`

Every tool follows the same pattern:

```python
import sys
from pathlib import Path

if __name__ == "__main__" and __package__ is None:
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    __package__ = "app"

from app import __version__
from app.core.<module> import <your_functions>
from app.utils.doc_reader import read_app_doc


def print_help():
    doc = read_app_doc("<name>")
    desc = doc.get("description", "<fallback description>")

    print(f"<name> - {desc}")
    print()
    print("USAGE:")
    print("    <name> [OPTIONS] <ARGS>")
    print()
    print("OPTIONS:")
    print("    -h, --help        Show help message")
    print("    -v, --version     Show version information")
    # ... your options ...


def print_version():
    doc = read_app_doc("<name>")
    print(doc.get("version", __version__))


def main():
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help", "help"):
        print_help()
        return 0

    if args[0] in ("-v", "--version"):
        print_version()
        return 0

    # ... your command logic ...

    return 0


if __name__ == "__main__":
    sys.exit(main())
```

### Key conventions

| Convention | Detail |
|------------|--------|
| **sys.path fix** | The `if __name__ == "__main__"` block at the top allows running as both `python app/main.py` and `python -m app.main` |
| **Manual arg parsing** | Use `sys.argv` directly — not `argparse` (keeps tools lightweight and consistent) |
| **`--help` and `--version`** | Always support `-h`/`--help` and `-v`/`--version` |
| **Exit codes** | Return `0` for success, non-zero for errors |
| **`read_app_doc`** | Load help text and version from `doc/<name>.yaml` |
| **`__version__`** | Defined in `app/__init__.py` — serves as fallback |

---

## 5. The Version — `app/__init__.py`

```python
__version__ = "0.1.0"
```

Keep this in sync with `.program` and `doc/<name>.yaml`.

---

## 6. Core Logic — `app/core/`

Put your tool's business logic here. Keep `main.py` thin — it should only parse arguments and call into core modules.

```
app/core/
├── __init__.py
└── <module>.py      # Your main logic
```

Example for a tool called `pyng`:

```
app/core/
├── __init__.py
├── pinger.py        # ICMP/TCP ping engine
└── formatter.py     # Colorized output formatting
```

### Rules

- **Pure Python only** — standard library, no `pip` dependencies
- **No I/O in core** — core functions should return data, not print directly (when practical)
- **Cross-platform** — test on macOS and Linux at minimum

---

## 7. The Doc Reader — `app/utils/doc_reader.py`

Every tool includes the same doc reader utility:

```python
import re
import sys
from pathlib import Path


def read_app_doc(app_name):
    """Read app documentation from YAML file."""
    doc_paths = [
        Path(__file__).parent.parent.parent.parent / "doc" / f"{app_name}.yaml",
        Path("doc") / f"{app_name}.yaml",
    ]

    if hasattr(sys, '_MEIPASS'):
        doc_paths.insert(0, Path(sys._MEIPASS) / "doc" / f"{app_name}.yaml")

    for path in doc_paths:
        if path.exists():
            try:
                content = path.read_text()

                version = re.search(
                    r'^VERSION:\s*"([^"]+)"', content, re.MULTILINE,
                )
                version = version.group(1) if version else ''

                desc = re.search(
                    '^DESCRIPTION:\\s*>\\s*(.+?)(?=^[A-Z_]+:)',
                    content,
                    re.MULTILINE | re.DOTALL,
                )
                desc = desc.group(1).strip() if desc else ''

                usage_section = re.search(
                    '^USAGE:(.+?)^OPTIONS:',
                    content,
                    re.MULTILINE | re.DOTALL,
                )
                usage = (
                    re.findall(r'-\s*"([^"]+)"', usage_section.group(1))
                    if usage_section
                    else []
                )

                return {
                    'version': version,
                    'description': desc,
                    'usage': usage,
                }
            except (OSError, UnicodeDecodeError):
                continue

    return {}
```

This is intentionally a simple regex-based YAML parser — no external YAML library needed.

---

## 8. Documentation — `doc/<name>.yaml`

This structured YAML file powers `--help`, `--version`, and the `doc` tool.

```yaml
NAME: <name>
VERSION: "0.1.0"
DESCRIPTION: >
  One or two sentences describing what the tool does and why.
  Mention the Unix equivalent if applicable.
USAGE:
  - "<name> [OPTIONS] <ARGS>"
  - "<name> --help"
  - "<name> --version"
OPTIONS:
  - "-h, --help        Show help message"
  - "-v, --version     Show version information"
  # ... your options ...
EXAMPLES:
  - "<name> example_arg               # Basic usage"
  - "<name> -o output.txt input.txt   # With options"
OUTPUT: >
  Describe what the tool outputs. Mention exit codes.
AUTHOR: "<your-handle>"
DATE: "<YYYY-MM-DD>"
NOTES:
  - "Any important notes about behavior."
  - "Mention platform-specific details."
  - "Pure Python — no external dependencies."
```

### Field reference

| Field | Required | Description |
|-------|----------|-------------|
| `NAME` | Yes | Tool name (no subtitle) |
| `VERSION` | Yes | Quoted string, e.g., `"0.1.0"` |
| `DESCRIPTION` | Yes | Folded block (`>`), 1-3 sentences |
| `USAGE` | Yes | List of usage patterns |
| `OPTIONS` | Yes | List of flag descriptions |
| `EXAMPLES` | Yes | List of example commands with comments |
| `OUTPUT` | Recommended | What the tool prints / exit codes |
| `AUTHOR` | Yes | Your GitHub handle |
| `DATE` | Yes | Creation date |
| `NOTES` | Recommended | Platform notes, limitations, tips |

---

## 9. Tests — `test/test_main.py`

Use `unittest` from the standard library:

```python
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.<module> import <your_functions>


class TestCoreFunctionality(unittest.TestCase):

    def test_basic_behavior(self):
        result = your_function()
        self.assertIsNotNone(result)

    def test_edge_case(self):
        # ...
        pass


if __name__ == "__main__":
    unittest.main()
```

### What to test

- Core logic functions (the `app/core/` modules)
- Edge cases and error handling
- Output formatting (with `color=False`)
- DNS/network functions should handle failure gracefully

---

## 10. CI/CD Workflows

### `test.yml` — Lint + Test + Build

```yaml
name: Test <name>

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    - name: Run blue
      run: |
        git clone --depth 1 https://github.com/Pynosaur/blue.git /tmp/blue
        cd /tmp/blue && python app/main.py $GITHUB_WORKSPACE

  test:
    needs: lint
    runs-on: {% raw %}${{ matrix.os }}{% endraw %}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest]
        python-version: ['3.8', '3.11', '3.12']

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python {% raw %}${{ matrix.python-version }}{% endraw %}
      uses: actions/setup-python@v5
      with:
        python-version: {% raw %}'${{ matrix.python-version }}'{% endraw %}

    - name: Test basic commands
      run: |
        python app/main.py --version
        python app/main.py --help

    - name: Run unit tests
      run: |
        python test/test_main.py

  build:
    runs-on: macos-latest
    needs: test

    steps:
    - uses: actions/checkout@v4

    - name: Set up Bazel
      uses: bazel-contrib/setup-bazel@0.8.1
      with:
        bazelisk-cache: true

    - name: Build with Bazel
      run: |
        bazel build //:<name>_bin
      continue-on-error: true

    - name: Test built binary
      if: success()
      run: |
        if [ -f ./bazel-bin/<name> ]; then
          ./bazel-bin/<name> --version
          ./bazel-bin/<name> --help
          echo "Built binary works"
        else
          echo "Binary not built, skipping test"
        fi
```

### `release.yml` — Auto-release

```yaml
name: Release

on:
  push:
    branches: [main]
    paths:
      - 'app/**'
      - 'doc/**'
      - '.program'

permissions:
  contents: write

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Get version
        id: version
        run: |
          version=$(grep '^version:' .program | cut -d' ' -f2)
          name=$(grep '^name:' .program | cut -d' ' -f2)
          echo "version=$version" >> "$GITHUB_OUTPUT"
          echo "name=$name" >> "$GITHUB_OUTPUT"
          echo "tag=v$version" >> "$GITHUB_OUTPUT"

      - name: Create release
        env:
          GH_TOKEN: {% raw %}${{ secrets.GITHUB_TOKEN }}{% endraw %}
        run: |
          tag="{% raw %}${{ steps.version.outputs.tag }}{% endraw %}"
          name="{% raw %}${{ steps.version.outputs.name }}{% endraw %}"
          version="{% raw %}${{ steps.version.outputs.version }}{% endraw %}"
          if gh release view "$tag" > /dev/null 2>&1; then
            gh release edit "$tag" \
              --title "$name $version" \
              --notes "Release $name $version"
          else
            gh release create "$tag" \
              --title "$name $version" \
              --notes "Release $name $version" \
              --latest
          fi
```

When you push changes to `app/`, `doc/`, or `.program` on `main`, this workflow reads the version from `.program` and creates (or updates) a GitHub release tagged `v<version>`.

---

## 11. Build Configuration

### `BUILD` — Bazel + Nuitka

```python
genrule(
    name = "<name>_bin",
    srcs = glob(["app/**/*.py", "doc/**/*.yaml"]),
    outs = ["<name>"],
    cmd = """
        /opt/homebrew/bin/nuitka \
            --onefile \
            --include-data-dir=doc=doc \
            --onefile-tempdir-spec=/tmp/nuitka-<name> \
            --no-progressbar \
            --assume-yes-for-downloads \
            --no-deployment-flag=self-execution \
            --output-dir=$$(dirname $(location <name>)) \
            --output-filename=<name> \
            $(location app/main.py)
    """,
    local = 1,
    visibility = ["//visibility:public"],
)
```

### `MODULE.bazel`

```python
module(
    name = "<name>",
    version = "0.1.0",
)

bazel_dep(name = "rules_python", version = "0.40.0")

python = use_extension("@rules_python//python/extensions:python.bzl", "python")
python.toolchain(python_version = "3.11")
```

---

## 12. Other Required Files

### `.gitignore`

```
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
dist/
*.egg-info/
.eggs/
bazel-*
MODULE.bazel.lock
.bazelrc
*.spec
.DS_Store
```

### `LICENSE`

Use the MIT License. Copy from any existing Pynosaur tool.

### `.githooks/pre-commit`

```bash
#!/bin/sh
if command -v blue > /dev/null 2>&1; then
    blue .
    if [ $? -ne 0 ]; then
        echo "pre-commit: blue found issues. Fix them or commit with --no-verify."
        exit 1
    fi
fi
```

Make it executable: `chmod +x .githooks/pre-commit`

Then configure git to use it: `git config core.hooksPath .githooks`

---

## 13. README.md

Follow this template:

```markdown
# <name>

One-sentence description.

## Install

pget install <name>

Or from source:

python app/main.py <args>

## Usage

# Basic usage
<name> <args>

# With options
<name> -o output <args>

# Show help
<name> --help

## Options

-h, --help       Show help
-v, --version    Show version
...

## Tests

python test/test_main.py

## License

MIT
```

---

## 14. Making It Discoverable

For your tool to appear on [pynosaur.org](https://pynosaur.org) and work with `pget`:

### A. Create the GitHub repository

1. Create the repo under the **Pynosaur** organization: `github.com/Pynosaur/<name>`
2. Push your code to the `main` branch
3. Ensure `.program` exists at the repo root on `main`

### B. Sidebar auto-discovery

The pynosaur.org sidebar fetches repos from the Pynosaur org via the GitHub API and checks for `.program` in each repo. If `.program` exists, the tool appears automatically — **no manual configuration needed**.

### C. Documentation page on pynosaur.org

To add a full documentation page (README content rendered at `pynosaur.org/<name>/`):

1. Add your tool to the `tools` dict in the [pynosaur site workflow](https://github.com/Pynosaur/pynosaur/blob/main/.github/workflows/pages.yml):

```python
tools = {
    # ... existing tools ...
    '<name>': '<name> - Short Description',
}
```

2. Create a placeholder page at `pages/<name>.md`:

```yaml
---
layout: default
title: "<name> - Short Description"
permalink: /<name>/
---
```

3. The CI workflow will fetch your `README.md` from GitHub and inject it into the page during deployment.

### D. Tools catalog

Add your tool to `docs/index.md` following the existing format:

```markdown
### [<name>](/<name>/) — Short Description
Description of what the tool does and why it is useful.
- **Equivalent:** `<unix-tool>`
- **Install:** `pget install <name>`
```

---

## Checklist

Use this checklist before submitting your tool:

- [ ] `.program` exists with `name`, `version`, `author`, `description`, `type`
- [ ] `app/__init__.py` has `__version__` matching `.program`
- [ ] `app/main.py` supports `--help` and `--version`
- [ ] `app/main.py` uses the `sys.path` fix at the top
- [ ] `doc/<name>.yaml` has all required fields
- [ ] `app/utils/doc_reader.py` is included
- [ ] `test/test_main.py` has passing tests
- [ ] `blue .` reports no issues
- [ ] `.github/workflows/test.yml` is configured
- [ ] `.github/workflows/release.yml` is configured
- [ ] `BUILD` file has the correct genrule name
- [ ] `MODULE.bazel` is configured
- [ ] `LICENSE` is MIT
- [ ] `README.md` documents usage and options
- [ ] `.gitignore` excludes `__pycache__/`, `bazel-*`, etc.
- [ ] `.githooks/pre-commit` runs blue
- [ ] Tool uses **only** the Python standard library
- [ ] Tool works on macOS and Linux
- [ ] Exit codes are correct (0 = success, non-zero = error)

---

## Example

See any existing tool for a complete reference:

| Tool | Description | Complexity |
|------|-------------|------------|
| [yday](https://github.com/Pynosaur/yday) | Day of year | Simple — good starting point |
| [see](https://github.com/Pynosaur/see) | File viewer | Medium — file I/O + formatting |
| [sock](https://github.com/Pynosaur/sock) | Socket tool | Complex — networking + subcommands |
| [pget](https://github.com/Pynosaur/pget) | Package manager | Advanced — GitHub API + installer |
