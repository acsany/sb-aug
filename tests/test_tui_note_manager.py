"""Tests for TUI NoteManager."""

from datetime import datetime
from pathlib import Path

import pytest

from secondbrain.tui.managers.note_manager import NoteManager


@pytest.fixture
def note_manager(tmp_path) -> NoteManager:
    """Create a NoteManager with a temporary directory."""
    return NoteManager(notes_dir=tmp_path)


class TestNoteManager:
    """Test NoteManager operations."""

    def test_get_all_notes_empty(self, note_manager) -> None:
        """Test get_all_notes on empty directory."""
        notes = note_manager.get_all_notes()
        assert notes == []

    def test_get_all_notes_single(self, note_manager, tmp_path) -> None:
        """Test get_all_notes with one note."""
        note_file = tmp_path / "2026-08-02-hello.md"
        note_file.write_text("# Hello\n")

        notes = note_manager.get_all_notes()

        assert len(notes) == 1
        assert notes[0].title == "Hello"
        assert notes[0].path == note_file
        assert notes[0].display_name == "2026-08-02 | Hello"

    def test_get_all_notes_sorted_newest_first(self, note_manager, tmp_path) -> None:
        """Test notes are sorted newest first."""
        (tmp_path / "2026-08-01-old.md").write_text("# Old\n")
        (tmp_path / "2026-08-03-newest.md").write_text("# Newest\n")
        (tmp_path / "2026-08-02-middle.md").write_text("# Middle\n")

        notes = note_manager.get_all_notes()

        assert len(notes) == 3
        assert notes[0].title == "Newest"
        assert notes[1].title == "Middle"
        assert notes[2].title == "Old"

    def test_get_note_content(self, note_manager, tmp_path) -> None:
        """Test reading note content."""
        note_file = tmp_path / "2026-08-02-test.md"
        content = "# Test Note\n\nSome content here."
        note_file.write_text(content, encoding="utf-8")

        result = note_manager.get_note_content(note_file)

        assert result == content

    def test_get_note_content_missing_file(self, note_manager) -> None:
        """Test reading non-existent file returns empty string."""
        missing = Path("/tmp/nonexistent-note-xyz.md")

        result = note_manager.get_note_content(missing)

        assert result == ""

    def test_create_new_note(self, note_manager, tmp_path) -> None:
        """Test creating a new note."""
        metadata = note_manager.create_new_note("My Test Note")

        assert metadata.title == "My Test Note"
        assert metadata.path.parent == tmp_path
        assert metadata.path.exists()
        assert metadata.display_name.endswith("| My Test Note")

        content = note_manager.get_note_content(metadata.path)
        assert "# My Test Note" in content

    def test_create_new_note_invalidates_cache(self, note_manager, tmp_path) -> None:
        """Test creating a note invalidates cache."""
        note_manager.get_all_notes()
        initial_count = len(note_manager.get_all_notes())

        note_manager.create_new_note("New Note")

        new_count = len(note_manager.get_all_notes())
        assert new_count == initial_count + 1

    def test_invalidate_cache(self, note_manager, tmp_path) -> None:
        """Test cache invalidation."""
        note_manager.get_all_notes()
        assert note_manager._cache is not None

        note_manager.invalidate_cache()
        assert note_manager._cache is None

    def test_extract_title_from_stem_basic(self) -> None:
        """Test title extraction from basic stem."""
        stem = "2026-08-02-hello-world"
        title = NoteManager._extract_title_from_stem(stem)
        assert title == "Hello World"

    def test_extract_title_from_stem_with_counter(self) -> None:
        """Test title extraction with counter suffix."""
        stem = "2026-08-02-hello-world--1"
        title = NoteManager._extract_title_from_stem(stem)
        assert title == "Hello World"

    def test_extract_title_from_stem_no_title(self) -> None:
        """Test extraction with no title part."""
        stem = "2026-08-02"
        title = NoteManager._extract_title_from_stem(stem)
        assert title == "Untitled"

    def test_extract_date_from_stem_valid(self) -> None:
        """Test date extraction from stem."""
        stem = "2026-08-02-hello"
        date = NoteManager._extract_date_from_stem(stem)
        assert date.year == 2026
        assert date.month == 8
        assert date.day == 2

    def test_extract_date_from_stem_invalid_falls_back_to_now(self) -> None:
        """Test invalid date extraction falls back to now."""
        stem = "invalid-date-stem"
        date = NoteManager._extract_date_from_stem(stem)
        # Just check it returns a datetime, not the exact value since "now" changes
        assert isinstance(date, datetime)

    def test_notes_dir_creation(self, tmp_path) -> None:
        """Test that notes_dir is created on first access."""
        notes_dir = tmp_path / "new_notes_dir"
        manager = NoteManager(notes_dir=notes_dir)

        assert not notes_dir.exists()

        manager.get_all_notes()

        assert notes_dir.exists()
