"""Tests for TUI application."""

from pathlib import Path

import pytest

from secondbrain.tui.app import SecondBrainTUI
from secondbrain.tui.models.app_state import ViewMode


@pytest.fixture
def tui_app(tmp_path) -> SecondBrainTUI:
    """Create a TUI app instance with temp notes directory."""
    app = SecondBrainTUI(debug=False, notes_dir=tmp_path)
    return app


class TestSecondBrainTUI:
    """Test SecondBrainTUI app."""

    def test_app_initialization(self, tui_app) -> None:
        """Test app initializes with correct defaults."""
        assert tui_app.state.mode == ViewMode.BROWSING
        assert tui_app.state.notes == []
        assert tui_app.state.selected_index is None

    def test_app_title(self, tui_app) -> None:
        """Test app has correct title."""
        assert tui_app.title == "Second Brain"

    def test_extract_title_from_markdown_heading(self) -> None:
        """Test extracting title from markdown heading."""
        content = "# My Note Title\n\nSome content here"
        title = SecondBrainTUI._extract_title_from_content(content)
        assert title == "My Note Title"

    def test_extract_title_from_first_line(self) -> None:
        """Test extracting title from first non-empty line."""
        content = "My First Line\n\nOther content"
        title = SecondBrainTUI._extract_title_from_content(content)
        assert title == "My First Line"

    def test_extract_title_empty_content(self) -> None:
        """Test extracting title from empty content."""
        content = ""
        title = SecondBrainTUI._extract_title_from_content(content)
        assert title == "Untitled"

    def test_extract_title_whitespace_only(self) -> None:
        """Test extracting title from whitespace-only content."""
        content = "   \n\n   "
        title = SecondBrainTUI._extract_title_from_content(content)
        assert title == "Untitled"

    def test_action_cancel_in_browsing_mode(self, tui_app) -> None:
        """Test cancel action has no effect in browsing mode."""
        assert tui_app.state.mode == ViewMode.BROWSING

        tui_app.action_cancel()

        assert tui_app.state.mode == ViewMode.BROWSING

    def test_update_status(self, tui_app) -> None:
        """Test status update includes mode and note count."""
        tui_app.state.notes = [None, None]
        tui_app._update_status()

        assert "BROWSING" in tui_app.sub_title
        assert "2 notes" in tui_app.sub_title

    def test_update_status_creating_mode(self, tui_app) -> None:
        """Test status shows CREATING mode."""
        tui_app.state.mode = ViewMode.CREATING
        tui_app.state.notes = []
        tui_app._update_status()

        assert "CREATING" in tui_app.sub_title

    def test_app_compose(self, tui_app) -> None:
        """Test app composes correct widgets."""
        widgets = list(tui_app.compose())
        widget_types = {type(w).__name__ for w in widgets}

        assert "Header" in widget_types
        assert "MainScreen" in widget_types
        assert "Footer" in widget_types

    def test_bindings(self, tui_app) -> None:
        """Test app has correct key bindings."""
        bindings = {b[0]: b[1] for b in tui_app.BINDINGS}

        assert bindings.get("ctrl+n") == "new_note"
        assert bindings.get("ctrl+s") == "save_note"
        assert bindings.get("escape") == "cancel"
        assert bindings.get("ctrl+q") == "quit"
