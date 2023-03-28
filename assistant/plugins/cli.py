import curses
import math

from assistant.message_bus.client import TextMessageClient


class CursesClient:
    def __init__(self, message_client: TextMessageClient) -> None:
        self.log_buffer = []
        self.text_buffer = []
        self.message_client = message_client

    def run(self):
        curses.wrapper(self._curses_runner)

    def _curses_runner(
        self,
        stdscr: curses.window,
    ):  # pylint: disable=too-many-locals,too-many-statements,too-many-branches
        # Set up the screen
        curses.curs_set(0)
        stdscr.nodelay(1)
        stdscr.timeout(100)
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_CYAN)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_CYAN)

        # Initialize variables
        input_buffer = []
        scroll_pos = 0

        # Calculate dimensions
        screen_height, screen_width = stdscr.getmaxyx()
        screen_height = (
            screen_height - 2
        )  # Can't write all the way to the bottom of the screen, especially in tmux
        assistant_line = 0
        separator_line = 1
        text_height = math.floor(screen_height * 0.75) - separator_line - 1
        log_height = screen_height - text_height - separator_line - 3
        log_separator_line = separator_line + text_height + 1
        input_separator_line = screen_height - 1
        input_line = screen_height

        while True:
            for message in self.message_client.read_message():
                self.text_buffer.append("Assistant: " + message)
                self.log_buffer.append("<out> " + message)

            # Clear screen
            stdscr.clear()

            # Draw Assistant title and separator
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(assistant_line, 0, "Assistant".center(screen_width))
            stdscr.addstr(separator_line, 0, "=" * screen_width)
            stdscr.attroff(curses.color_pair(1))

            # Draw dividers
            stdscr.attron(curses.color_pair(2))
            stdscr.addstr(log_separator_line, 0, "-" * screen_width)
            stdscr.addstr(input_separator_line, 0, "-" * screen_width)
            stdscr.attroff(curses.color_pair(2))

            # Display text buffer
            for i, line in enumerate(
                self.text_buffer[scroll_pos : scroll_pos + text_height]
            ):
                stdscr.addstr(separator_line + 1 + i, 0, line[:screen_width])

            # Display log buffer
            for i, line in enumerate(self.log_buffer[-log_height:]):
                stdscr.addstr(log_separator_line + 1 + i, 0, line[:screen_width])

            # Display input buffer
            stdscr.addstr(
                input_line,
                0,
                "> "
                + "".join(input_buffer).ljust(screen_width - 2)[-(screen_width - 2) :],
            )

            # Refresh screen
            stdscr.refresh()

            # Get user input
            key = stdscr.getch()

            # Exit on CTRL-C or CTRL-D
            if key in (3, 4):
                break

            # Backspace
            if key in (127, 8):
                if input_buffer:
                    input_buffer.pop()

            # Enter
            elif key == 10:
                self.text_buffer.append("User: " + "".join(input_buffer))
                self.log_buffer.append("<in>  " + "".join(input_buffer))
                self.message_client.send_message("".join(input_buffer))
                input_buffer.clear()

            # Up arrow
            elif key == curses.KEY_UP:
                scroll_pos = max(0, scroll_pos - 1)

            # Down arrow
            elif key == curses.KEY_DOWN:
                scroll_pos = min(len(self.text_buffer) - text_height, scroll_pos + 1)

            # Page Up
            elif key == curses.KEY_PPAGE:
                scroll_pos = max(0, scroll_pos - text_height)

            # Page Down
            elif key == curses.KEY_NPAGE:
                scroll_pos = min(
                    len(self.text_buffer) - text_height, scroll_pos + text_height
                )

            # Regular characters
            elif key != -1:
                input_buffer.append(chr(key))
