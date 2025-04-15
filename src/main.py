#!/usr/bin/env python3
"""
SimpleEditor: A basic text editor with a gap buffer implementation
- No curses dependency for easier debugging
- Fully type-hinted for better code understanding
"""

import os
import sys
from typing import List, Optional, Tuple


class GapBuffer:
    """
    A gap buffer implementation for efficient text editing.

    The gap buffer is a data structure that maintains a "gap" in the buffer to make
    insertions and deletions more efficient by minimizing data movement.
    """

    def __init__(self, text: str = ""):
        """
        Initialize the gap buffer with optional text.

        Args:
            text: Initial text to place in the buffer
        """
        # The actual character buffer with pre-allocated space for the gap
        self.buffer: List[str] = list(text) + [" "] * 100

        # Index where the gap starts (right after the text)
        self.gap_start: int = len(text)

        # Index where the gap ends (end of the buffer)
        self.gap_end: int = len(self.buffer)

    def move_gap(self, pos: int) -> None:
        """
        Move the gap to the specified position.

        This involves moving characters around to relocate the gap without changing
        the visible content of the buffer.

        Args:
            pos: The position to move the gap to
        """
        if pos == self.gap_start:
            return  # Gap is already at the desired position

        if pos < self.gap_start:
            # Moving gap left: move characters between pos and gap_start to the end of the gap
            dist = self.gap_start - pos
            self.buffer[self.gap_end - dist : self.gap_end] = self.buffer[
                pos : self.gap_start
            ]
            self.gap_start = pos
            self.gap_end -= dist
        else:
            # Moving gap right: move characters between gap_end and pos to the start of the gap
            dist = pos - self.gap_start
            self.buffer[self.gap_start : self.gap_start + dist] = self.buffer[
                self.gap_end : self.gap_end + dist
            ]
            self.gap_start = pos
            self.gap_end += dist

    def insert(self, pos: int, char: str) -> None:
        """
        Insert a character at the specified position.

        Args:
            pos: Position to insert at
            char: Character to insert
        """
        if self.gap_end == self.gap_start:
            # Gap is empty, resize the buffer
            self.buffer.extend([" "] * 100)
            self.gap_end += 100

        # Move the gap to the insertion point
        self.move_gap(pos)

        # Insert the character at the start of the gap
        self.buffer[self.gap_start] = char

        # Shrink the gap from the left
        self.gap_start += 1

    def delete(self, pos: int) -> None:
        """
        Delete a character at the specified position.

        Args:
            pos: Position to delete from
        """
        if pos < 0 or pos >= len(self.buffer) - (self.gap_end - self.gap_start):
            return  # Position out of bounds

        # Position the gap for deletion
        if pos < self.gap_start:
            self.move_gap(pos)
        elif pos >= self.gap_end:
            self.move_gap(pos + 1)

        # Expand the gap from the left to "delete" the character
        self.gap_end += 1

    def get_text(self) -> str:
        """
        Get the text content as a string by concatenating before and after the gap.

        Returns:
            The complete text in the buffer
        """
        return "".join(self.buffer[: self.gap_start] + self.buffer[self.gap_end :])

    def get_line(self, line_idx: int) -> str:
        """
        Get a specific line from the buffer.

        Args:
            line_idx: Index of the line to retrieve

        Returns:
            The specified line as a string, or empty string if out of range
        """
        text = self.get_text()
        lines = text.split("\n")
        if 0 <= line_idx < len(lines):
            return lines[line_idx]
        return ""

    def get_lines(self) -> List[str]:
        """
        Get all lines from the buffer.

        Returns:
            List of all text lines
        """
        return self.get_text().split("\n")

    def get_line_count(self) -> int:
        """
        Get the number of lines in the buffer.

        Returns:
            The total number of lines
        """
        return self.get_text().count("\n") + 1


class SimpleEditor:
    """
    A simple text editor that supports basic editing operations.

    This version does not use curses, making it easier to debug.
    """

    def __init__(self, filename: Optional[str] = None):
        """
        Initialize the editor, optionally loading a file.

        Args:
            filename: Path to the file to edit (if any)
        """
        # The gap buffer containing the text being edited
        self.buffer: GapBuffer = GapBuffer()

        # The path to the file being edited (if any)
        self.filename: Optional[str] = filename

        # Current cursor coordinates (column, row)
        self.cursor_x: int = 0
        self.cursor_y: int = 0

        # Load file if provided
        if filename and os.path.exists(filename):
            with open(filename, "r") as f:
                self.buffer = GapBuffer(f.read())

    def save_file(self) -> bool:
        """
        Save the current buffer to a file.

        Returns:
            True if save was successful, False otherwise
        """
        if not self.filename:
            print("No filename specified")
            return False

        try:
            with open(self.filename, "w") as f:
                f.write(self.buffer.get_text())
            print(f"Saved to {self.filename}")
            return True
        except Exception as e:
            print(f"Error saving file: {str(e)}")
            return False

    def get_cursor_position(self) -> int:
        """
        Get the absolute position of the cursor in the buffer.

        This converts the 2D cursor position (cursor_x, cursor_y) into
        a 1D position in the buffer.

        Returns:
            The absolute cursor position in the buffer
        """
        pos = 0
        lines = self.buffer.get_lines()

        # Add lengths of all previous lines
        for i in range(self.cursor_y):
            if i < len(lines):
                pos += len(lines[i]) + 1  # +1 for newline

        # Add the x position
        pos += min(
            self.cursor_x,
            len(lines[self.cursor_y]) if self.cursor_y < len(lines) else 0,
        )
        return pos

    def insert_char(self, char: str) -> None:
        """
        Insert a character at the current cursor position.

        Args:
            char: The character to insert
        """
        pos = self.get_cursor_position()
        self.buffer.insert(pos, char)
        self.cursor_x += 1

    def insert_newline(self) -> None:
        """Insert a newline at the current cursor position."""
        pos = self.get_cursor_position()
        self.buffer.insert(pos, "\n")
        self.cursor_y += 1
        self.cursor_x = 0

    def delete_char(self) -> None:
        """Delete the character before the cursor position."""
        if self.cursor_x > 0:
            # Middle of line
            pos = self.get_cursor_position() - 1
            self.buffer.delete(pos)
            self.cursor_x -= 1
        elif self.cursor_y > 0:
            # Beginning of line, join with previous line
            lines = self.buffer.get_lines()
            prev_line_len = len(lines[self.cursor_y - 1])
            pos = self.get_cursor_position() - 1
            self.buffer.delete(pos)
            self.cursor_y -= 1
            self.cursor_x = prev_line_len

    def move_cursor(self, dx: int, dy: int) -> None:
        """
        Move the cursor by the specified delta.

        Args:
            dx: Change in x position
            dy: Change in y position
        """
        new_y = self.cursor_y + dy

        # Validate y position
        if new_y >= 0 and new_y < self.buffer.get_line_count():
            self.cursor_y = new_y

            # Get length of the current line
            current_line = self.buffer.get_line(self.cursor_y)
            line_length = len(current_line)

            # Adjust x position
            new_x = self.cursor_x + dx
            if new_x < 0:
                new_x = 0
            elif new_x > line_length:
                new_x = line_length

            self.cursor_x = new_x

    def display_buffer(self) -> None:
        """
        Display the current buffer content and cursor position.
        This is a debug version that prints to the console.
        """
        lines = self.buffer.get_lines()
        print("\n--- Buffer Content ---")
        for i, line in enumerate(lines):
            cursor_marker = ""
            if i == self.cursor_y:
                # Insert cursor marker
                if self.cursor_x <= len(line):
                    cursor_marker = f" (cursor at position {self.cursor_x})"
            print(f"{i + 1}: {line}{cursor_marker}")
        print("---------------------")
        print(
            f"Cursor: ({self.cursor_x}, {self.cursor_y}), Buffer position: {self.get_cursor_position()}"
        )
        print(f"Gap: {self.buffer.gap_start} - {self.buffer.gap_end}")

    def run_debug_session(self) -> None:
        """
        Run a simple debug loop for testing the editor functionality.
        This provides a simple command interface instead of a visual editor.
        """
        print("Simple Text Editor Debug Session")
        print(
            "Commands: i [char] (insert), d (delete), n (newline), "
            + "u (up), d (down), l (left), r (right), s (save), q (quit)"
        )

        while True:
            self.display_buffer()
            command = input("Command: ").strip()

            if not command:
                continue

            if command == "q":
                break
            elif command == "s":
                self.save_file()
            elif command.startswith("i ") and len(command) > 2:
                self.insert_char(command[2])
            elif command == "d":
                self.delete_char()
            elif command == "n":
                self.insert_newline()
            elif command == "u":
                self.move_cursor(0, -1)
            elif command == "down":
                self.move_cursor(0, 1)
            elif command == "l":
                self.move_cursor(-1, 0)
            elif command == "r":
                self.move_cursor(1, 0)
            else:
                print("Unknown command")


def main() -> None:
    """
    Main function to run the editor.
    """
    filename = sys.argv[1] if len(sys.argv) > 1 else None
    editor = SimpleEditor(filename)

    # Run the debug-friendly command interface
    editor.run_debug_session()


if __name__ == "__main__":
    main()
