import os
import curses
import sys
from typing import Optional


class SimpleEditor:
    def __init__(self, stdscr: curses.window, filename: Optional[str] = None):
        """
        Initializes the editor.

        :param stdscr: The main curses window (stands for "standard screen").
        :param filename: Optional filename to load into the buffer.
        """
        self.stdscr: curses.window = stdscr
        self.filename: Optional[str] = filename
        self.cursor_y: int = 0
        self.cursor_x: int = 0
        self.buffer: list[str] = list()  # Each line of the file is a string in this list

        if filename:
            self.load_file(filename)

    def load_file(self, filename: str) -> None:
        """Load a file into the buffer line by line."""
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                self.buffer = f.readlines()
        else:
            with open(filename, "w", encoding="utf-8") as f:
                f.write("")
        if not self.buffer:
            self.buffer.append("")  # Ensure there's at least one empty line

        # load on screen the file contents
        for ch in "".join(self.buffer):
            self.insert_char(ch=ch)

    def save_file(self) -> None:
        """Save the buffer to the file."""
        print("DEBUG: inside `save_file`")
        print(f"self.buffer: {self.buffer}")

        if self.filename:
            with open(self.filename, "w", encoding="utf-8") as f:
                f.writelines(self.buffer)

    def insert_char(self, ch: str) -> None:
        """Insert a character at the cursor position."""
        while len(self.buffer) <= self.cursor_y:
            self.buffer.append("")

        line = self.buffer[self.cursor_y]

        left = line[:self.cursor_x]
        right = line[self.cursor_x:]

        if ch != curses.KEY_ENTER:
            self.buffer[self.cursor_y] = left + ch + right
            self.cursor_x += 1
        else:
            self.buffer[self.cursor_y] = left
            self.buffer.insert(self.cursor_y + 1, right)
            self.cursor_y += 1
            self.cursor_x = 0

    def delete_char(self) -> None:
        """Delete a character before the cursor."""
        if self.cursor_x > 0:
            line = self.buffer[self.cursor_y]
            self.buffer[self.cursor_y] = (
                line[: self.cursor_x - 1] + line[self.cursor_x :]
            )
            self.cursor_x -= 1

    def run(self) -> None:
        """Main editor loop."""
        curses.curs_set(1)  # Make the cursor visible
        self.stdscr.timeout(100)  # Set a timeout for non-blocking input

        while True:
            self.stdscr.clear()  # Clear the screen before drawing
            h, w = self.stdscr.getmaxyx()  # Get terminal height and width

            # Draw buffer contents to screen
            for idx, line in enumerate(self.buffer[:h]):
                self.stdscr.addstr(idx, 0, line[:w])  # Limit to screen width

            # Move cursor to current position
            self.stdscr.move(self.cursor_y, self.cursor_x)
            self.stdscr.refresh()

            # Wait for key input
            ch = self.stdscr.getch()
            if ch == -1:
                continue  # No input, just refresh

            # === Handle input ===
            match ch:
                case 27:  # ESC to quit
                    break
                case 19:  # Ctrl+S to save
                    self.save_file()
                case curses.KEY_BACKSPACE | 127:
                    self.delete_char()
                case 10:  # Enter key
                    line = self.buffer[self.cursor_y]
                    left = line[:self.cursor_x]
                    right = line[self.cursor_x:]
                    self.buffer[self.cursor_y] = left
                    self.buffer.insert(self.cursor_y + 1, right)
                    self.cursor_y += 1
                    self.cursor_x = 0
                case curses.KEY_LEFT:
                    self.cursor_x = max(0, self.cursor_x - 1)
                case curses.KEY_RIGHT:
                    self.cursor_x = min(len(self.buffer[self.cursor_y]), self.cursor_x + 1)
                case curses.KEY_UP:
                    self.cursor_y = max(0, self.cursor_y - 1)
                    self.cursor_x = min(len(self.buffer[self.cursor_y]), self.cursor_x)
                case curses.KEY_DOWN:
                    self.cursor_y = min(len(self.buffer) - 1, self.cursor_y + 1)
                    self.cursor_x = min(len(self.buffer[self.cursor_y]), self.cursor_x)
                case ch if 32 <= ch < 127:  # Printable ASCII characters
                    self.insert_char(chr(ch))

def main(stdscr: curses.window) -> None:
    """
    This is the entry point for curses. stdscr is the standard screen buffer.
    """
    filename = sys.argv[1] if len(sys.argv) > 1 else None
    editor = SimpleEditor(stdscr, filename)
    editor.run()


if __name__ == "__main__":
    # curses.wrapper handles initialization and cleanup of the terminal
    curses.wrapper(main)
