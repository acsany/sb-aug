"""Application state models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path


class ViewMode(Enum):
    """Application view mode state."""

    BROWSING = "browsing"
    CREATING = "creating"


@dataclass
class NoteMetadata:
    """Metadata for a note in the list."""

    index: int
    path: Path
    title: str
    created: datetime
    display_name: str


@dataclass
class AppState:
    """Central application state."""

    mode: ViewMode = ViewMode.BROWSING
    notes: list[NoteMetadata] = field(default_factory=list)
    selected_index: int | None = None
    editor_content: str = ""
    current_note_path: Path | None = None

    def reset_editor(self) -> None:
        """Clear editor content and path."""
        self.editor_content = ""
        self.current_note_path = None

    def select_note(self, index: int) -> None:
        """Select a note by index."""
        if 0 <= index < len(self.notes):
            self.selected_index = index
            self.current_note_path = self.notes[index].path
