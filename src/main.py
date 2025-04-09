import os
import curses
import sys
import logging
from typing import Optional

# Set up logging for debugging
logging.basicConfig(filename='editor_debug.log', level=logging.DEBUG)


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
        self.buffer: list[str] = [""]  # Start with one empty line
        self.status_message = ""

        if filename:
            self.load_file(filename)

    def load_file(self, filename: str) -> None:
        """Load a file into the buffer line by line."""
        try:
            if os.path.exists(filename):
                with open(filename, "r", encoding="utf-8") as f:
                    content = f.read()
                    # Split by newlines and ensure lines don't contain \n characters
                    self.buffer = [line for line in content.splitlines()]
            else:
                # Create new file if it doesn't exist
                self.buffer = [""]  # Start with one empty line
                self.status_message = f"New file: {filename}"

            # Ensure there's at least one line in the buffer
            if not self.buffer:
                self.buffer = [""]

            logging.debug(f"Loaded buffer: {self.buffer}")
        except Exception as e:
            self.status_message = f"Error loading file: {str(e)}"
            logging.error(f"Error loading file: {str(e)}")

    def save_file(self) -> None:
        """Save the buffer to the file."""
        try:
            if self.filename:
                with open(self.filename, "w", encoding="utf-8") as f:
                    # Join lines with newlines
                    content = "\n".join(self.buffer)
                    f.write(content)
                self.status_message = f"Saved to: {self.filename}"
                logging.debug(f"Saved buffer: {self.buffer}")
            else:
                self.status_message = "No filename specified"
        except Exception as e:
            self.status_message = f"Error saving: {str(e)}"
            logging.error(f"Error saving: {str(e)}")

    def insert_char(self, ch: str) -> None:
        """Insert a character at the cursor position."""
        # Ensure buffer has enough lines
        while len(self.buffer) <= self.cursor_y:
            self.buffer.append("")

        line = self.buffer[self.cursor_y]

        # Insert character at cursor position
        self.buffer[self.cursor_y] = line[:self.cursor_x] + \
            ch + line[self.cursor_x:]
        self.cursor_x += 1

    def delete_char(self) -> None:
        """Delete a character before the cursor."""
        if self.cursor_x > 0:
            line = self.buffer[self.cursor_y]
            self.buffer[self.cursor_y] = line[:self.cursor_x - 1] + \
                line[self.cursor_x:]
            self.cursor_x -= 1
        elif self.cursor_y > 0:  # At beginning of line, join with previous line
            prev_line = self.buffer[self.cursor_y - 1]
            current_line = self.buffer[self.cursor_y]
            self.cursor_x = len(prev_line)
            self.buffer[self.cursor_y - 1] = prev_line + current_line
            self.buffer.pop(self.cursor_y)
            self.cursor_y -= 1

    def handle_enter(self) -> None:
        """Handle the Enter key by splitting the current line at the cursor."""
        current_line = self.buffer[self.cursor_y]
        left_part = current_line[:self.cursor_x]
        right_part = current_line[self.cursor_x:]

        self.buffer[self.cursor_y] = left_part
        self.buffer.insert(self.cursor_y + 1, right_part)

        self.cursor_y += 1
        self.cursor_x = 0

    def run(self) -> None:
        """Main editor loop."""
        curses.curs_set(1)  # Make the cursor visible
        self.stdscr.timeout(100)  # Set a timeout for non-blocking input
        self.stdscr.keypad(True)  # Enable special keys

        while True:
            self.stdscr.clear()  # Clear the screen before drawing
            h, w = self.stdscr.getmaxyx()  # Get terminal height and width

            # Draw buffer contents to screen
            # Leave one line for status
            for idx, line in enumerate(self.buffer[:h-1]):
                try:
                    # Limit to screen width
                    self.stdscr.addstr(idx, 0, line[:w-1])
                except curses.error:
                    # This can happen when writing to the bottom-right corner
                    pass

            # Show status message
            try:
                if self.status_message:
                    status = self.status_message[:w-1]
                else:
                    status = f"{self.filename or 'Untitled'} | Line {
                        self.cursor_y+1}/{len(self.buffer)}"
                self.stdscr.addstr(h-1, 0, status, curses.A_REVERSE)
            except curses.error:
                pass

            # Move cursor to current position
            try:
                self.stdscr.move(self.cursor_y, self.cursor_x)
            except curses.error:
                # Adjust cursor if it's outside visible area
                self.cursor_x = min(self.cursor_x, w-2)

            self.stdscr.refresh()

            # Wait for key input
            try:
                ch = self.stdscr.getch()
            except curses.error:
                continue

            if ch == -1:
                continue  # No input, just refresh

            # === Handle input ===
            if ch == 27:  # ESC to quit
                break
            # Ctrl+S to save
            elif ch == 19 or ch == ord('s') and curses.keyname(ch).decode().startswith("^"):
                self.save_file()
            elif ch in (curses.KEY_BACKSPACE, 127, 8):  # Backspace
                self.delete_char()
            elif ch == 10 or ch == curses.KEY_ENTER:  # Enter key
                self.handle_enter()
            elif ch == curses.KEY_LEFT:
                if self.cursor_x > 0:
                    self.cursor_x -= 1
                elif self.cursor_y > 0:
                    # Move to end of previous line
                    self.cursor_y -= 1
                    self.cursor_x = len(self.buffer[self.cursor_y])
            elif ch == curses.KEY_RIGHT:
                if self.cursor_x < len(self.buffer[self.cursor_y]):
                    self.cursor_x += 1
                elif self.cursor_y < len(self.buffer) - 1:
                    # Move to beginning of next line
                    self.cursor_y += 1
                    self.cursor_x = 0
            elif ch == curses.KEY_UP:
                if self.cursor_y > 0:
                    self.cursor_y -= 1
                    self.cursor_x = min(self.cursor_x, len(
                        self.buffer[self.cursor_y]))
            elif ch == curses.KEY_DOWN:
                if self.cursor_y < len(self.buffer) - 1:
                    self.cursor_y += 1
                    self.cursor_x = min(self.cursor_x, len(
                        self.buffer[self.cursor_y]))
            elif 32 <= ch < 127:  # Printable ASCII characters
                self.insert_char(chr(ch))

            # Clear status message after any key press
            if ch != -1:
                self.status_message = ""


def main(stdscr: curses.window) -> None:
    """
    This is the entry point for curses. stdscr is the standard screen buffer.
    """
    # Setup terminal
    curses.start_color()
    curses.use_default_colors()

    # Get filename from command line argument
    filename = sys.argv[1] if len(sys.argv) > 1 else None

    # Initialize editor
    editor = SimpleEditor(stdscr, filename)
    editor.run()


if __name__ == "__main__":
    # curses.wrapper handles initialization and cleanup of the terminal
    curses.wrapper(main)
