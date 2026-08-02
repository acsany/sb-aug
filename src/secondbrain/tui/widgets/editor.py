"""Markdown editor widget."""

from __future__ import annotations

from textual.containers import Container
from textual.widgets import TextArea

from textual.message import Message


class EditorChanged(Message):
    """Posted when editor content changes."""

    def __init__(self, content: str) -> None:
        """Initialize with new content."""
        super().__init__()
        self.content = content


class MarkdownEditor(Container):
    """Markdown editor pane."""

    DEFAULT_CSS = """
    MarkdownEditor {
        height: 1fr;
        border: solid $accent;
        padding: 0;
    }

    MarkdownEditor > TextArea {
        height: 1fr;
        width: 100%;
    }
    """

    def __init__(self, **kwargs) -> None:
        """Initialize editor."""
        super().__init__(**kwargs)
        self.text_area = TextArea(language="markdown")
        self.read_only = False

    def compose(self):
        """Render the text area."""
        yield self.text_area

    def on_mount(self) -> None:
        """Set up editor after mount."""
        self.text_area.read_only = self.read_only

    def set_content(self, content: str) -> None:
        """Set editor content."""
        self.text_area.text = content

    def get_content(self) -> str:
        """Get current editor content."""
        return self.text_area.text

    def clear(self) -> None:
        """Clear editor content."""
        self.text_area.text = ""

    def set_read_only(self, read_only: bool) -> None:
        """Set read-only mode."""
        self.read_only = read_only
        self.text_area.read_only = read_only

    def focus_editor(self) -> None:
        """Focus the text area."""
        self.text_area.focus()

    def set_placeholder(self, text: str) -> None:
        """Set placeholder text (visual only, handled by app)."""
        pass
