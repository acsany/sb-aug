"""Note list sidebar widget."""

from __future__ import annotations

from textual.containers import Container
from textual.message import Message
from textual.widgets import ListItem, ListView

from secondbrain.tui.models.app_state import NoteMetadata


class NoteSelected(Message):
    """Posted when a note is selected."""

    def __init__(self, index: int) -> None:
        """Initialize with note index."""
        super().__init__()
        self.index = index


class NoteListItem(ListItem):
    """A single note in the list."""

    def __init__(self, note: NoteMetadata) -> None:
        """Initialize with note metadata."""
        super().__init__()
        self.note = note
        self.label = note.display_name


class NoteList(Container):
    """Scrollable list of notes in sidebar."""

    DEFAULT_CSS = """
    NoteList {
        height: 1fr;
        border: solid $accent;
        padding: 0;
    }

    NoteList > ListView {
        height: 1fr;
        width: 100%;
    }
    """

    def __init__(self, **kwargs) -> None:
        """Initialize empty note list."""
        super().__init__(**kwargs)
        self.list_view = ListView()

    def compose(self):
        """Render the list view."""
        yield self.list_view

    def on_mount(self) -> None:
        """Set up event handlers."""
        pass

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle note selection from ListView."""
        if isinstance(event.item, NoteListItem):
            self.post_message(NoteSelected(event.item.note.index))

    def set_notes(self, notes: list[NoteMetadata]) -> None:
        """Update the note list."""
        self.list_view.clear()
        for note in notes:
            item = NoteListItem(note)
            self.list_view.append(item)

    def select_by_index(self, index: int) -> None:
        """Select a note by index."""
        if 0 <= index < len(self.list_view.children):
            self.list_view.index = index
