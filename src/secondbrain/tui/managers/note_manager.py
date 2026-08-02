"""Orchestrates access to notes."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from loguru import logger

from secondbrain import notes
from secondbrain.tui.models.app_state import NoteMetadata


class NoteManager:
    """Manages note operations via secondbrain.notes."""

    def __init__(self, notes_dir: Path | None = None) -> None:
        """Initialize note manager.

        Args:
            notes_dir: Override default notes directory (for testing).
        """
        self.notes_dir = notes_dir or notes.notes_dir()
        self._cache: list[NoteMetadata] | None = None

    def get_all_notes(self) -> list[NoteMetadata]:
        """Get all notes from disk, sorted by date (newest first)."""
        if self._cache is not None:
            return self._cache

        self.notes_dir.mkdir(parents=True, exist_ok=True)
        note_files = sorted(self.notes_dir.glob("*.md"), reverse=True)

        result: list[NoteMetadata] = []
        for index, path in enumerate(note_files):
            try:
                stem = path.stem
                title = self._extract_title_from_stem(stem)
                created = self._extract_date_from_stem(stem)
                display_name = f"{created.strftime('%Y-%m-%d')} | {title}"

                result.append(
                    NoteMetadata(
                        index=index,
                        path=path,
                        title=title,
                        created=created,
                        display_name=display_name,
                    )
                )
            except Exception as e:
                logger.debug(f"Error parsing note {path}: {e}")
                continue

        self._cache = result
        return result

    def get_note_content(self, path: Path) -> str:
        """Read note content."""
        try:
            return notes.read_note(path)
        except Exception as e:
            logger.error(f"Error reading note {path}: {e}")
            return ""

    def create_new_note(self, title: str) -> NoteMetadata:
        """Create a new note and return its metadata."""
        created = datetime.now()
        path = notes.create_note(title, self.notes_dir, created)
        self.invalidate_cache()

        display_name = f"{created.strftime('%Y-%m-%d')} | {title}"
        return NoteMetadata(
            index=0,
            path=path,
            title=title,
            created=created,
            display_name=display_name,
        )

    def invalidate_cache(self) -> None:
        """Clear the note list cache."""
        self._cache = None

    @staticmethod
    def _extract_title_from_stem(stem: str) -> str:
        """Extract title from filename stem (YYYY-MM-DD-title[--counter])."""
        parts = stem.split("-", 3)
        if len(parts) >= 4:
            title_part = parts[3]
            if "--" in title_part:
                title_part = title_part.split("--")[0]
            return title_part.replace("-", " ").title()
        return "Untitled"

    @staticmethod
    def _extract_date_from_stem(stem: str) -> datetime:
        """Extract date from filename stem (YYYY-MM-DD-...)."""
        parts = stem.split("-")
        if len(parts) >= 3:
            try:
                year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
                return datetime(year, month, day)
            except (ValueError, IndexError):
                pass
        return datetime.now()
