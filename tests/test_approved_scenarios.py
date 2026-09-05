"""
Approved Scenarios runner.

Reads every tests/approved/*.approved.md fixture, runs the command it declares,
regenerates the three result sections (退出码 / 标准输出 / 标准错误) from the
actual run, and asserts the regenerated text equals the file on disk.

Review is a markdown diff, never assertion code. Set APPROVE=1 to rewrite the
fixtures with actual output (then review `git diff`).
"""
import os
import re
import shlex
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

APPROVED_DIR = Path(__file__).parent / 'approved'
# Result sections are regenerated; every other section is the human-authored fact.
RESULT_SECTIONS = ('退出码', '标准输出', '标准错误')


def _sections(text, heading):
    """Yield (whole_match, fenced_body) for each '## <heading>' block."""
    pattern = re.compile(
        r'^## %s[^\n]*\n\n```[a-z]*\n(.*?)```' % re.escape(heading),
        re.MULTILINE | re.DOTALL,
    )
    return pattern


def _run(fixture_text, workdir):
    for match in _sections(fixture_text, '输入').finditer(fixture_text):
        name = re.search(r'`([^`]+)`', match.group(0)).group(1)
        (workdir / name).write_text(match.group(1), newline='')

    command = _sections(fixture_text, '命令').search(fixture_text).group(1).strip()
    argv = shlex.split(command)
    argv[:1] = [sys.executable, '-m', 'csvkit.utilities.%s' % argv[0]]

    completed = subprocess.run(argv, cwd=workdir, capture_output=True, text=True)
    return {
        '退出码': '%d\n' % completed.returncode,
        '标准输出': completed.stdout.replace('\r\n', '\n'),
        '标准错误': completed.stderr.replace('\r\n', '\n'),
    }


def _regenerate(fixture_text, actual):
    for heading in RESULT_SECTIONS:
        match = _sections(fixture_text, heading).search(fixture_text)
        body = actual[heading]
        replacement = match.group(0)[:match.start(1) - match.start(0)] + body + '```'
        fixture_text = fixture_text[:match.start()] + replacement + fixture_text[match.end():]
    return fixture_text


class TestApprovedScenarios(unittest.TestCase):
    pass


def _make_test(path):
    def test(self):
        approved = path.read_text()
        with tempfile.TemporaryDirectory() as tmp:
            actual = _run(approved, Path(tmp))
        received = _regenerate(approved, actual)

        if os.environ.get('APPROVE'):
            path.write_text(received)
            return
        if received != approved:
            path.with_suffix('.received.md').write_text(received)
            self.fail(
                '%s: actual output differs from the approved facts.\n'
                'Inspect %s, or rerun with APPROVE=1 to accept and review the diff.'
                % (path.name, path.with_suffix('.received.md').name)
            )
        path.with_suffix('.received.md').unlink(missing_ok=True)
    return test


for _path in sorted(APPROVED_DIR.glob('*.approved.md')):
    setattr(TestApprovedScenarios, 'test_%s' % _path.name.split('.')[0].replace('-', '_'), _make_test(_path))
