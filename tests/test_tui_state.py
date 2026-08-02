"""Tests for TUI state models."""

import pytest

from secondbrain.tui.models.app_state import AppState, NoteMetadata, ViewMode


class TestViewMode:
    """Test ViewMode enum."""

    def test_browsing_mode(self) -> None:
        """Test BROWSING mode value."""
        assert ViewMode.BROWSING.value == "browsing"

    def test_creating_mode(self) -> None:
        """Test CREATING mode value."""
        assert ViewMode.CREATING.value == "creating"


class TestNoteMetadata:
    """Test NoteMetadata dataclass."""

    def test_note_metadata_creation(self, tmp_path) -> None:
        """Test creating a NoteMetadata instance."""
        from datetime import datetime

        path = tmp_path / "2026-08-02-test.md"
        created = datetime(2026, 8, 2)

        metadata = NoteMetadata(
            index=0,
            path=path,
            title="Test Note",
            created=created,
            display_name="2026-08-02 | Test Note",
        )

        assert metadata.index == 0
        assert metadata.path == path
        assert metadata.title == "Test Note"
        assert metadata.created == created
        assert metadata.display_name == "2026-08-02 | Test Note"


class TestAppState:
    """Test AppState dataclass and transitions."""

    def test_initial_state(self) -> None:
        """Test default AppState initialization."""
        state = AppState()

        assert state.mode == ViewMode.BROWSING
        assert state.notes == []
        assert state.selected_index is None
        assert state.editor_content == ""
        assert state.current_note_path is None

    def test_reset_editor(self) -> None:
        """Test reset_editor clears content and path."""
        from pathlib import Path

        state = AppState(
            editor_content="Some text",
            current_note_path=Path("/tmp/note.md"),
        )

        state.reset_editor()

        assert state.editor_content == ""
        assert state.current_note_path is None

    def test_select_note_valid_index(self, tmp_path) -> None:
        """Test selecting a note by valid index."""
        from datetime import datetime
        from pathlib import Path

        note1_path = tmp_path / "2026-08-02-first.md"
        note2_path = tmp_path / "2026-08-01-second.md"

        metadata1 = NoteMetadata(
            index=0,
            path=note1_path,
            title="First",
            created=datetime(2026, 8, 2),
            display_name="2026-08-02 | First",
        )
        metadata2 = NoteMetadata(
            index=1,
            path=note2_path,
            title="Second",
            created=datetime(2026, 8, 1),
            display_name="2026-08-01 | Second",
        )

        state = AppState(notes=[metadata1, metadata2])
        state.select_note(1)

        assert state.selected_index == 1
        assert state.current_note_path == note2_path

    def test_select_note_invalid_index(self, tmp_path) -> None:
        """Test selecting with out-of-bounds index does nothing."""
        from datetime import datetime

        note_path = tmp_path / "2026-08-02-test.md"
        metadata = NoteMetadata(
            index=0,
            path=note_path,
            title="Test",
            created=datetime(2026, 8, 2),
            display_name="2026-08-02 | Test",
        )

        state = AppState(notes=[metadata])
        state.select_note(10)

        assert state.selected_index is None
        assert state.current_note_path is None

    def test_select_note_negative_index(self, tmp_path) -> None:
        """Test selecting with negative index does nothing."""
        from datetime import datetime

        note_path = tmp_path / "2026-08-02-test.md"
        metadata = NoteMetadata(
            index=0,
            path=note_path,
            title="Test",
            created=datetime(2026, 8, 2),
            display_name="2026-08-02 | Test",
        )

        state = AppState(notes=[metadata])
        state.select_note(-1)

        assert state.selected_index is None
        assert state.current_note_path is None
