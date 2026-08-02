"""Create note button widget."""

from __future__ import annotations

from textual.containers import Container
from textual.message import Message
from textual.widgets import Button


class CreateButtonPressed(Message):
    """Posted when create button is pressed."""

    pass


class CreateButton(Container):
    """Create new note button (fixed at bottom of sidebar)."""

    DEFAULT_CSS = """
    CreateButton {
        height: auto;
        border: solid $accent;
        padding: 0 1;
    }

    CreateButton > Button {
        width: 100%;
    }
    """

    def __init__(self, **kwargs) -> None:
        """Initialize button."""
        super().__init__(**kwargs)
        self.button = Button("+ New Note")

    def compose(self):
        """Render the button."""
        yield self.button

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button == self.button:
            self.post_message(CreateButtonPressed())
