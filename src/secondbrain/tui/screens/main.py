"""Main two-pane screen."""

from __future__ import annotations

from textual.containers import Container, Horizontal
from textual.widgets import Footer, Header, Static

from secondbrain.tui.widgets.create_button import CreateButton
from secondbrain.tui.widgets.editor import MarkdownEditor
from secondbrain.tui.widgets.note_list import NoteList


class Sidebar(Container):
    """Left sidebar containing note list and create button."""

    DEFAULT_CSS = """
    Sidebar {
        width: 30;
        height: 1fr;
        layout: vertical;
    }

    Sidebar > NoteList {
        height: 1fr;
    }

    Sidebar > CreateButton {
        height: auto;
    }
    """

    def compose(self):
        """Render sidebar components."""
        yield NoteList(id="note-list")
        yield CreateButton(id="create-button")


class ContentPane(Container):
    """Right side content pane with editor."""

    DEFAULT_CSS = """
    ContentPane {
        height: 1fr;
        width: 1fr;
    }
    """

    def compose(self):
        """Render content pane."""
        yield MarkdownEditor(id="editor")


class MainScreen(Container):
    """Main two-pane layout screen."""

    DEFAULT_CSS = """
    MainScreen {
        layout: horizontal;
        height: 100%;
        width: 100%;
    }

    MainScreen > Sidebar {
        height: 100%;
    }

    MainScreen > ContentPane {
        height: 100%;
    }
    """

    def compose(self):
        """Render main layout."""
        yield Sidebar(id="sidebar")
        yield ContentPane(id="content-pane")

    def get_note_list(self) -> NoteList:
        """Get reference to note list widget."""
        return self.query_one("#note-list", NoteList)

    def get_editor(self) -> MarkdownEditor:
        """Get reference to editor widget."""
        return self.query_one("#editor", MarkdownEditor)

    def get_create_button(self) -> CreateButton:
        """Get reference to create button widget."""
        return self.query_one("#create-button", CreateButton)
