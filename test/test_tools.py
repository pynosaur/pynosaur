"""Validate _data/tools.yml against tool repos and pages."""

import re
import unittest
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS_YML = ROOT / '_data' / 'tools.yml'
PAGES_DIR = ROOT / 'pages'
GITHUB_ORG = 'pynosaur'


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


def fetch_program_version(tool_name: str) -> str:
    """Fetch .program version from GitHub, fall back to local sibling."""
    local = ROOT.parent / tool_name / '.program'
    if local.exists():
        text = local.read_text(encoding='utf-8')
        for line in text.split('\n'):
            if line.startswith('version:'):
                return line.split(':', 1)[1].strip()

    url = (
        f'https://raw.githubusercontent.com/'
        f'{GITHUB_ORG}/{tool_name}/main/.program'
    )
    try:
        response = urllib.request.urlopen(url, timeout=10)
        text = response.read().decode('utf-8')
        for line in text.split('\n'):
            if line.startswith('version:'):
                return line.split(':', 1)[1].strip()
    except Exception:
        pass

    return ''


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

    def test_versions_match_program(self):
        mismatches = []
        for entry in self.entries:
            prog_version = fetch_program_version(entry['name'])
            if not prog_version:
                continue
            if entry['version'] != prog_version:
                mismatches.append(
                    f'{entry["name"]}: tools.yml={entry["version"]} '
                    f'.program={prog_version}'
                )

        self.assertEqual(
            mismatches, [],
            f'Version mismatches:\n  ' + '\n  '.join(mismatches)
            if mismatches else '',
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
