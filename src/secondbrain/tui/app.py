"""Main TUI application."""

from __future__ import annotations

from pathlib import Path

from loguru import logger
from textual.app import ComposeResult, App
from textual.widgets import Footer, Header

from secondbrain.tui.managers.note_manager import NoteManager
from secondbrain.tui.models.app_state import AppState, ViewMode
from secondbrain.tui.screens.main import MainScreen
from secondbrain.tui.widgets.create_button import CreateButtonPressed
from secondbrain.tui.widgets.note_list import NoteSelected


class SecondBrainTUI(App):
    """Terminal UI for secondbrain note management."""

    CSS = """
    Screen {
        layout: vertical;
    }

    Header {
        height: 1;
        background: $accent;
        color: $text;
    }

    Footer {
        height: auto;
        background: $accent;
        color: $text;
    }
    """

    BINDINGS = [
        ("ctrl+n", "new_note", "New"),
        ("ctrl+s", "save_note", "Save"),
        ("escape", "cancel", "Cancel"),
        ("ctrl+q", "quit", "Quit"),
    ]

    def __init__(self, debug: bool = False, notes_dir: Path | None = None) -> None:
        """Initialize TUI application.

        Args:
            debug: Enable debug logging.
            notes_dir: Override notes directory (for testing).
        """
        super().__init__()
        self.debug_mode = debug
        self.state = AppState()
        self.note_manager = NoteManager(notes_dir=notes_dir)
        self.title = "Second Brain"

    def compose(self) -> ComposeResult:
        """Create app layout."""
        yield Header()
        yield MainScreen(id="main-screen")
        yield Footer()

    def on_mount(self) -> None:
        """Initialize app on mount."""
        self._load_notes()
        self._setup_bindings()

    def on_note_selected(self, message: NoteSelected) -> None:
        """Handle note selection from sidebar."""
        self.state.select_note(message.index)
        self._update_editor_content()

    def on_create_button_pressed(self, message: CreateButtonPressed) -> None:
        """Handle create button press."""
        self.action_new_note()

    def action_new_note(self) -> None:
        """Action: create new note."""
        logger.debug("Creating new note")
        self.state.mode = ViewMode.CREATING
        self.state.reset_editor()
        self.state.editor_content = ""

        editor = self._get_editor()
        editor.set_read_only(False)
        editor.clear()
        editor.focus_editor()

        self._update_status()

    def action_save_note(self) -> None:
        """Action: save current note."""
        if self.state.mode == ViewMode.CREATING:
            logger.debug("Saving new note")
            content = self._get_editor().get_content()

            if not content.strip():
                logger.debug("Cannot save empty note")
                return

            title = self._extract_title_from_content(content)
            try:
                self.note_manager.create_new_note(title)
                self._load_notes()
                self.state.mode = ViewMode.BROWSING
                self._update_editor_content()
            except Exception as e:
                logger.error(f"Error saving note: {e}")

    def action_cancel(self) -> None:
        """Action: cancel editing."""
        if self.state.mode in (ViewMode.CREATING,):
            logger.debug("Canceling edit")
            self.state.mode = ViewMode.BROWSING
            self.state.reset_editor()
            self._update_editor_content()

    def action_quit(self) -> None:
        """Action: quit application."""
        self.exit()

    def _load_notes(self) -> None:
        """Load notes from disk."""
        logger.debug("Loading notes")
        self.state.notes = self.note_manager.get_all_notes()
        self._get_note_list().set_notes(self.state.notes)

    def _update_editor_content(self) -> None:
        """Update editor with current note or empty."""
        editor = self._get_editor()

        if self.state.mode == ViewMode.BROWSING:
            if self.state.current_note_path:
                content = self.note_manager.get_note_content(
                    self.state.current_note_path
                )
                editor.set_content(content)
            else:
                editor.clear()
            editor.set_read_only(True)
        else:
            editor.set_read_only(False)

        self._update_status()

    def _update_status(self) -> None:
        """Update status/title bar."""
        mode_text = self.state.mode.value.upper()
        note_count = len(self.state.notes)
        self.sub_title = f"{mode_text} | {note_count} notes"

    def _setup_bindings(self) -> None:
        """Set up keyboard bindings."""
        pass

    def _get_main_screen(self) -> MainScreen:
        """Get main screen widget."""
        return self.query_one("#main-screen", MainScreen)

    def _get_note_list(self):
        """Get note list widget."""
        return self._get_main_screen().get_note_list()

    def _get_editor(self):
        """Get editor widget."""
        return self._get_main_screen().get_editor()

    @staticmethod
    def _extract_title_from_content(content: str) -> str:
        """Extract title from note content (first line or first # heading)."""
        lines = content.strip().split("\n")
        for line in lines:
            line = line.strip()
            if line.startswith("# "):
                return line[2:].strip()
            elif line and not line.startswith("#"):
                return line
        return "Untitled"
