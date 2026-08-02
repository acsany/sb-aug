"""Integration tests for TUI app interactions."""

from pathlib import Path

import pytest

from secondbrain.tui.app import SecondBrainTUI
from secondbrain.tui.models.app_state import ViewMode

pytestmark = pytest.mark.asyncio


@pytest.fixture
def tui_app(tmp_path) -> SecondBrainTUI:
    """Create a TUI app instance with temp notes directory."""
    return SecondBrainTUI(debug=False, notes_dir=tmp_path)


class TestTUISaveNote:
    """Test saving notes through the TUI."""

    async def test_save_new_note(self, tui_app, tmp_path) -> None:
        """Test creating and saving a new note."""
        async with tui_app.run_test() as pilot:
            await pilot.pause()

            # Start creating a new note
            tui_app.action_new_note()
            assert tui_app.state.mode == ViewMode.CREATING

            # Set editor content
            editor = tui_app._get_editor()
            editor.set_content("# My Test Note\n\nThis is test content.")

            # Save the note
            tui_app.action_save_note()

            # Verify we're back in browsing mode
            assert tui_app.state.mode == ViewMode.BROWSING

            # Verify the note was created
            notes = list(tmp_path.glob("*.md"))
            assert len(notes) == 1

            # Verify the content was saved
            content = notes[0].read_text(encoding="utf-8")
            assert "My Test Note" in content
            assert "This is test content" in content

    async def test_save_empty_note_ignored(self, tui_app, tmp_path) -> None:
        """Test that saving empty note is ignored."""
        async with tui_app.run_test() as pilot:
            await pilot.pause()

            tui_app.action_new_note()
            editor = tui_app._get_editor()
            editor.set_content("")

            tui_app.action_save_note()

            # No notes should be created
            notes = list(tmp_path.glob("*.md"))
            assert len(notes) == 0

    async def test_cancel_discards_content(self, tui_app) -> None:
        """Test that cancel discards editor content."""
        async with tui_app.run_test() as pilot:
            await pilot.pause()

            tui_app.action_new_note()
            editor = tui_app._get_editor()
            editor.set_content("Unsaved content")

            tui_app.action_cancel()

            # Should be back in browsing mode
            assert tui_app.state.mode == ViewMode.BROWSING
            assert tui_app.state.editor_content == ""


class TestTUIBrowsing:
    """Test browsing and viewing notes."""

    async def test_select_note_shows_content(self, tui_app, tmp_path) -> None:
        """Test selecting a note displays its content."""
        # Create test notes
        note1 = tmp_path / "2026-08-02-first.md"
        note1.write_text("# First Note\n\nFirst content")
        note2 = tmp_path / "2026-08-01-second.md"
        note2.write_text("# Second Note\n\nSecond content")

        async with tui_app.run_test() as pilot:
            await pilot.pause()

            # Notes should be loaded
            assert len(tui_app.state.notes) == 2

            # Select first note
            tui_app.state.select_note(0)
            editor = tui_app._get_editor()
            editor.set_content(tui_app.note_manager.get_note_content(tui_app.state.notes[0].path))

            # Verify editor shows correct content
            content = editor.get_content()
            assert "First Note" in content
            assert "First content" in content

    async def test_notes_sorted_newest_first(self, tui_app, tmp_path) -> None:
        """Test notes are displayed in newest-first order."""
        (tmp_path / "2026-08-01-old.md").write_text("# Old\n")
        (tmp_path / "2026-08-03-new.md").write_text("# New\n")
        (tmp_path / "2026-08-02-mid.md").write_text("# Mid\n")

        async with tui_app.run_test() as pilot:
            await pilot.pause()

            assert len(tui_app.state.notes) == 3
            assert tui_app.state.notes[0].title == "New"
            assert tui_app.state.notes[1].title == "Mid"
            assert tui_app.state.notes[2].title == "Old"
