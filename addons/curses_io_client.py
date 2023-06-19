import asyncio
import curses
import itertools
import math
import pathlib
import typing
import uuid

import aio_pika
from aiostream import stream  # type: ignore

from assistant.input import Input
from assistant.message import Message
from assistant.output import Output
from assistant.util import logging


async def tail_f(log_file: pathlib.Path):
    with log_file.open("r") as file:
        while line := file.readline():
            pass

        while True:
            line = file.readline()
            if line:
                yield line.strip()
            else:
                await asyncio.sleep(0.1)


async def tail_f_logs():
    tails = stream.merge(*[tail_f(log) for log in logging.LOG_DIR.glob("*.log")])
    async with tails.stream() as tail_stream:
        async for line in tail_stream:
            yield line


def tail(log_file: pathlib.Path):
    return log_file.read_text().splitlines()[:-100]


def tail_logs():
    return itertools.chain.from_iterable(
        tail(log) for log in logging.LOG_DIR.glob("*.log")
    )


class CursesIOClient:
    class _In(Input):
        def __init__(self, connection: aio_pika.Connection, queue: asyncio.Queue):
            super().__init__(connection)
            self.queue = queue
            self.conversation = str(uuid.uuid4())

        @staticmethod
        def name() -> str:
            return "curses-io-client"

        async def get_input(self) -> typing.Tuple[str, str, dict]:
            text = await self.queue.get()
            return text, self.conversation, {}

    class _Out(Output):
        def __init__(
            self,
            connection: aio_pika.Connection,
            message_buffer: typing.List[typing.Any],
        ):
            super().__init__(connection)
            self.message_buffer = message_buffer

        async def handle_message(self, msg: Message) -> None:
            self.message_buffer.append(f"<out> {msg.text}")

    def __init__(self, connection) -> None:
        self.inputs_queue: asyncio.Queue = asyncio.Queue()
        self.input = CursesIOClient._In(connection, self.inputs_queue)
        self.log_buffer = list(tail_logs())
        self.message_buffer: typing.List[str] = []
        self.output = CursesIOClient._Out(connection, self.message_buffer)

    async def run(self):
        await asyncio.gather(
            self.input.run(),
            self.output.run(),
            self.run_curses_ui(),
            self.run_tail_logs(),
        )

    async def run_tail_logs(self):
        async for line in tail_f_logs():
            self.log_buffer.append(line)

    async def run_curses_ui(
        self,
    ):  # pylint: disable=too-many-locals,too-many-statements,too-many-branches
        try:
            # Initialize curses, copied from curses.wrapper()
            stdscr = curses.initscr()
            curses.noecho()
            curses.cbreak()
            stdscr.keypad(1)
            curses.start_color()

            # Set up the screen
            curses.curs_set(0)
            stdscr.nodelay(True)
            stdscr.timeout(100)
            curses.start_color()
            curses.use_default_colors()
            curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_CYAN)
            curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_CYAN)

            # Calculate dimensions
            screen_height, screen_width = stdscr.getmaxyx()
            screen_height = (
                screen_height - 2
            )  # Can't write all the way to the bottom of the screen, especially in tmux
            assistant_line = 0
            separator_line = 1
            log_buffer_height = math.floor(screen_height * 0.666) - separator_line - 1
            log_buffer_separator_line = separator_line + log_buffer_height + 1
            message_buffer_height = (
                screen_height - log_buffer_height - separator_line - 3
            )
            input_separator_line = screen_height - 1
            input_line = screen_height

            # Initialize variables
            input_buffer = []
            scroll_pos = max(0, len(self.log_buffer) - log_buffer_height)
            tailing_logs = True

            while True:
                # Clear screen
                stdscr.clear()

                if tailing_logs:
                    scroll_pos = max(0, len(self.log_buffer) - log_buffer_height)

                # Draw Assistant title and separator
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(assistant_line, 0, "Assistant".center(screen_width))
                stdscr.addstr(separator_line, 0, "=" * screen_width)
                stdscr.attroff(curses.color_pair(1))

                # Draw dividers
                stdscr.attron(curses.color_pair(2))
                stdscr.addstr(log_buffer_separator_line, 0, "-" * screen_width)
                stdscr.addstr(input_separator_line, 0, "-" * screen_width)
                stdscr.attroff(curses.color_pair(2))

                # Display log buffer
                for i, line in enumerate(
                    self.log_buffer[scroll_pos : scroll_pos + log_buffer_height]
                ):
                    stdscr.addstr(separator_line + 1 + i, 0, str(line)[:screen_width])

                # Display message buffer
                for i, line in enumerate(self.message_buffer[-message_buffer_height:]):
                    stdscr.addstr(
                        log_buffer_separator_line + 1 + i,
                        0,
                        str(line).replace("\n", "\\n")[:screen_width],
                    )

                # Display input buffer
                stdscr.addstr(
                    input_line,
                    0,
                    "> "
                    + "".join(input_buffer).ljust(screen_width - 2)[
                        -(screen_width - 2) :
                    ],
                )

                # Refresh screen
                stdscr.refresh()

                # Get user input
                key = stdscr.getch()

                if key == curses.ERR:
                    await asyncio.sleep(
                        0.1
                    )  # Offer up the event loop to any other ready coroutines

                # Exit on CTRL-C or CTRL-D
                if key in (3, 4):
                    break

                # Backspace
                if key in (127, 8):
                    if input_buffer:
                        input_buffer.pop()

                # Enter
                elif key == 10:
                    self.message_buffer.append("<in>  " + "".join(input_buffer))
                    await self.inputs_queue.put("".join(input_buffer))
                    input_buffer.clear()

                # Up arrow
                elif key == curses.KEY_UP:
                    tailing_logs = False
                    scroll_pos = max(0, scroll_pos - 1)

                # Down arrow
                elif key == curses.KEY_DOWN:
                    scroll_pos = min(
                        len(self.log_buffer) - log_buffer_height, scroll_pos + 1
                    )
                    if scroll_pos == len(self.log_buffer) - log_buffer_height:
                        tailing_logs = True

                # Page Up
                elif key == curses.KEY_PPAGE:
                    tailing_logs = False
                    scroll_pos = max(0, scroll_pos - log_buffer_height)

                # Page Down
                elif key == curses.KEY_NPAGE:
                    scroll_pos = min(
                        len(self.log_buffer) - log_buffer_height,
                        scroll_pos + log_buffer_height,
                    )
                    if scroll_pos == len(self.log_buffer) - log_buffer_height:
                        tailing_logs = True

                # Regular characters
                elif key != -1:
                    input_buffer.append(chr(key))
        finally:
            # Cleanup curses
            stdscr.keypad(0)
            curses.echo()
            curses.nocbreak()
            curses.endwin()
