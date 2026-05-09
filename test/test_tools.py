"""Validate _data/tools.yml against tool repos and pages."""

import re
import unittest
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS_YML = ROOT / '_data' / 'tools.yml'
PAGES_DIR = ROOT / 'pages'
GITHUB_ORG = 'pynosaur'
GITHUB_RAW = 'https://raw.githubusercontent.com'


def parse_tools_yml(text: str) -> list:
    """Return list of dicts with name, version, line_no."""
    entries = []
    current_name = None
    current_version = None
    name_line = 0

    for i, line in enumerate(text.split('\n'), 1):
        stripped = line.strip()

        m = re.match(r'^-?\s*name:\s*(.+)$', stripped)
        if m:
            current_name = m.group(1).strip()
            name_line = i
            continue

        m = re.match(r'^version:\s*"?([^"]+)"?\s*$', stripped)
        if m and current_name is not None:
            current_version = m.group(1).strip()
            entries.append({
                'name': current_name,
                'version': current_version,
                'line': name_line,
            })
            current_name = None
            current_version = None

    return entries


def _fetch_file(tool_name: str, rel_path: str) -> str:
    """Read a file from a sibling repo, falling back to GitHub raw."""
    local = ROOT.parent / tool_name / rel_path
    if local.exists():
        return local.read_text(encoding='utf-8')

    url = f'{GITHUB_RAW}/{GITHUB_ORG}/{tool_name}/main/{rel_path}'
    try:
        response = urllib.request.urlopen(url, timeout=10)
        return response.read().decode('utf-8')
    except Exception:
        return ''


def fetch_program_version(tool_name: str) -> str:
    """Extract version from .program file."""
    text = _fetch_file(tool_name, '.program')
    for line in text.split('\n'):
        if line.startswith('version:'):
            return line.split(':', 1)[1].strip()
    return ''


def fetch_init_version(tool_name: str) -> str:
    """Extract __version__ from app/__init__.py."""
    text = _fetch_file(tool_name, 'app/__init__.py')
    m = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', text)
    return m.group(1) if m else ''


def fetch_doc_version(tool_name: str) -> str:
    """Extract VERSION from doc/<name>.yaml."""
    text = _fetch_file(tool_name, f'doc/{tool_name}.yaml')
    m = re.search(
        r'^VERSION:\s*"?([^"\n]+)"?\s*$',
        text,
        re.MULTILINE,
    )
    return m.group(1).strip() if m else ''


class TestToolsYml(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.text = TOOLS_YML.read_text(encoding='utf-8')
        cls.entries = parse_tools_yml(cls.text)

    def test_tools_yml_exists(self):
        self.assertTrue(
            TOOLS_YML.exists(),
            '_data/tools.yml not found',
        )

    def test_tools_yml_not_empty(self):
        self.assertGreater(
            len(self.entries), 0,
            '_data/tools.yml has no tool entries',
        )

    def test_each_tool_has_page(self):
        missing = []
        for entry in self.entries:
            page = PAGES_DIR / f'{entry["name"]}.md'
            if not page.exists():
                missing.append(entry['name'])

        self.assertEqual(
            missing, [],
            f'Tools missing pages/{{}}.md: {", ".join(missing)}',
        )

    def test_each_tool_has_program_marker(self):
        missing = []
        for entry in self.entries:
            prog_version = fetch_program_version(entry['name'])
            if not prog_version:
                missing.append(entry['name'])

        self.assertEqual(
            missing, [],
            f'Tools in tools.yml missing .program file: '
            f'{", ".join(missing)}',
        )

    def test_tools_yml_matches_program(self):
        mismatches = []
        for entry in self.entries:
            prog = fetch_program_version(entry['name'])
            if not prog:
                continue
            if entry['version'] != prog:
                mismatches.append(
                    f'{entry["name"]}: '
                    f'tools.yml={entry["version"]} '
                    f'.program={prog}'
                )

        self.assertEqual(
            mismatches, [],
            'tools.yml vs .program:\n  '
            + '\n  '.join(mismatches),
        )

    def test_init_version_matches_program(self):
        mismatches = []
        for entry in self.entries:
            prog = fetch_program_version(entry['name'])
            init = fetch_init_version(entry['name'])
            if not prog or not init:
                continue
            if init != prog:
                mismatches.append(
                    f'{entry["name"]}: '
                    f'__init__.py={init} '
                    f'.program={prog}'
                )

        self.assertEqual(
            mismatches, [],
            'app/__init__.py vs .program:\n  '
            + '\n  '.join(mismatches),
        )

    def test_doc_version_matches_program(self):
        mismatches = []
        for entry in self.entries:
            prog = fetch_program_version(entry['name'])
            doc = fetch_doc_version(entry['name'])
            if not prog or not doc:
                continue
            if doc != prog:
                mismatches.append(
                    f'{entry["name"]}: '
                    f'doc/{entry["name"]}.yaml={doc} '
                    f'.program={prog}'
                )

        self.assertEqual(
            mismatches, [],
            'doc/<name>.yaml vs .program:\n  '
            + '\n  '.join(mismatches),
        )

    def test_each_tool_has_init_version(self):
        missing = []
        for entry in self.entries:
            prog = fetch_program_version(entry['name'])
            init = fetch_init_version(entry['name'])
            if prog and not init:
                missing.append(entry['name'])

        self.assertEqual(
            missing, [],
            'Tools with .program but no __version__ in '
            f'app/__init__.py: {", ".join(missing)}',
        )

    def test_each_tool_has_doc_version(self):
        missing = []
        for entry in self.entries:
            prog = fetch_program_version(entry['name'])
            doc = fetch_doc_version(entry['name'])
            if prog and not doc:
                missing.append(entry['name'])

        self.assertEqual(
            missing, [],
            'Tools with .program but no VERSION in '
            f'doc/<name>.yaml: {", ".join(missing)}',
        )

    def test_entries_sorted_alphabetically(self):
        names = [e['name'] for e in self.entries]
        self.assertEqual(
            names, sorted(names),
            f'Tools are not sorted alphabetically: {names}',
        )

    def test_no_duplicate_entries(self):
        names = [e['name'] for e in self.entries]
        dupes = [n for n in names if names.count(n) > 1]
        self.assertEqual(
            dupes, [],
            f'Duplicate entries: {", ".join(set(dupes))}',
        )


if __name__ == '__main__':
    unittest.main()
