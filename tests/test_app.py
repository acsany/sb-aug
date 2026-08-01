import re

import pytest
from loguru import logger

from secondbrain.app import configure_logging, main

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
LINE_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} \| I \| secondbrain\.app:main:\d+ \| Hello from secondbrain!$"
)


def _last_line(text):
    """Return the last non-empty line of text, stripped of ANSI escape codes."""
    lines = [line for line in ANSI_RE.sub("", text).splitlines() if line.strip()]
    return lines[-1]


def test_main_logs_greeting(capfd):
    main()
    captured = capfd.readouterr()
    assert "Hello from secondbrain!" in captured.err


def test_console_line_matches_compact_format(capfd):
    main()
    line = _last_line(capfd.readouterr().err)
    assert LINE_RE.match(line), f"unexpected console line: {line!r}"


def test_console_line_has_no_milliseconds_or_dash_separator(capfd):
    main()
    line = _last_line(capfd.readouterr().err)
    assert not re.search(r"\d{2}:\d{2}:\d{2}\.\d+", line), f"milliseconds in: {line!r}"
    assert " - " not in line, f"dash separator in: {line!r}"


def test_file_line_matches_console_format(tmp_path):
    main()
    logger.remove()  # close and flush the file sink
    line = _last_line((tmp_path / "test.log").read_text())
    assert LINE_RE.match(line), f"unexpected file line: {line!r}"


@pytest.mark.parametrize(
    ("level", "icon"),
    [
        ("TRACE", "T"),
        ("DEBUG", "D"),
        ("INFO", "I"),
        ("SUCCESS", "S"),
        ("WARNING", "W"),
        ("ERROR", "E"),
        ("CRITICAL", "C"),
    ],
)
def test_level_icons_are_single_letters(level, icon):
    configure_logging()
    assert logger.level(level).icon == icon
