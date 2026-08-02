"""Tests for TUI widgets."""

from datetime import datetime
from pathlib import Path

import pytest

from secondbrain.tui.app import SecondBrainTUI
from secondbrain.tui.models.app_state import NoteMetadata
from secondbrain.tui.screens.main import MainScreen
from secondbrain.tui.widgets.note_list import NoteList

pytestmark = pytest.mark.asyncio


@pytest.fixture
def tui_app(tmp_path) -> SecondBrainTUI:
    """Create a TUI app instance with temp notes directory."""
    return SecondBrainTUI(debug=False, notes_dir=tmp_path)


class TestNoteListWidget:
    """Test NoteList widget."""

    async def test_note_list_set_notes(self, tui_app: SecondBrainTUI) -> None:
        """Test setting notes in the list."""
        async with tui_app.run_test() as pilot:
            note_list = tui_app._get_note_list()

            note1 = NoteMetadata(
                index=0,
                path=Path("/tmp/note1.md"),
                title="Note 1",
                created=datetime(2026, 8, 2),
                display_name="2026-08-02 | Note 1",
            )
            note2 = NoteMetadata(
                index=1,
                path=Path("/tmp/note2.md"),
                title="Note 2",
                created=datetime(2026, 8, 1),
                display_name="2026-08-01 | Note 2",
            )

            note_list.set_notes([note1, note2])

            assert len(note_list.list_view.children) == 2


class TestEditorWidget:
    """Test MarkdownEditor widget."""

    async def test_editor_set_content(self, tui_app: SecondBrainTUI) -> None:
        """Test setting editor content."""
        async with tui_app.run_test() as pilot:
            editor = tui_app._get_editor()

            content = "# Hello\n\nThis is a test note."
            editor.set_content(content)

            assert editor.get_content() == content

    async def test_editor_clear(self, tui_app: SecondBrainTUI) -> None:
        """Test clearing editor content."""
        async with tui_app.run_test() as pilot:
            editor = tui_app._get_editor()

            editor.set_content("Some content")
            editor.clear()

            assert editor.get_content() == ""

    async def test_editor_read_only_mode(self, tui_app: SecondBrainTUI) -> None:
        """Test setting read-only mode."""
        async with tui_app.run_test() as pilot:
            editor = tui_app._get_editor()

            editor.set_read_only(True)
            assert editor.text_area.read_only is True

            editor.set_read_only(False)
            assert editor.text_area.read_only is False


class TestMainScreenLayout:
    """Test MainScreen layout."""

    async def test_main_screen_has_sidebar(self, tui_app: SecondBrainTUI) -> None:
        """Test that main screen has sidebar."""
        async with tui_app.run_test() as pilot:
            main_screen = tui_app._get_main_screen()
            assert main_screen is not None

            sidebar = main_screen.query_one("#sidebar", MainScreen.__bases__[0])
            assert sidebar is not None

    async def test_main_screen_has_content_pane(
        self, tui_app: SecondBrainTUI
    ) -> None:
        """Test that main screen has content pane."""
        async with tui_app.run_test() as pilot:
            main_screen = tui_app._get_main_screen()
            assert main_screen is not None

            # Check that we can access the editor through the main screen
            editor = main_screen.get_editor()
            assert editor is not None


class TestAppIntegration:
    """Integration tests for app interactions."""

    async def test_app_loads_notes_on_mount(self, tui_app, tmp_path) -> None:
        """Test that app loads notes when mounted."""
        (tmp_path / "2026-08-02-test.md").write_text("# Test\n")

        async with tui_app.run_test() as pilot:
            await pilot.pause()
            assert len(tui_app.state.notes) == 1

    async def test_app_displays_notes_in_list(self, tui_app, tmp_path) -> None:
        """Test that notes are displayed in the list."""
        (tmp_path / "2026-08-02-hello.md").write_text("# Hello\n")
        (tmp_path / "2026-08-01-world.md").write_text("# World\n")

        async with tui_app.run_test() as pilot:
            await pilot.pause()
            note_list = tui_app._get_note_list()
            assert len(note_list.list_view.children) == 2
