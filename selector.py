#!/usr/bin/python
from __future__ import print_function
"""
Usage:
    selector.py
    selector.py -f=<filepath>
    selector.py -a=<filepath>
    selector.py -c=<command>
    selector.py -e=<command>

Options:
    -h --help                 Show this screen.
    -f=<filepath> --file      Write selected item as content of file
    -a=<filepath> --append    Append selected item to file
    -c=<command> --command    Execute unix command with after replacing "@" with selected item
    -e=<command> --echo       Execute unix command by echoing and pipeing selected item
"""
import curses
import re
from collections import namedtuple
from .fuzzy import filter


def select(options, initial_query='', make_complition=None):
    selector = Selector(options, initial_query, make_complition)
    return selector.run()


Selection = namedtuple(
    'Selection',
    ['index', 'typed', 'selected', 'options']
)


class Selector(object):
    """return (index of selection, typed text, selected text)."""
    COLOR_SEARCH_BOX = 5  # blue
    COLOR_SELECTION = 6  # magenta
    ESCAPE = 27
    ENTER = ord("\n")
    SPACE = ord(" ")
    subitem_prefix = "  "
    separator = ""
    start_list_line = 2
    empty_result = Selection(None, None, None, None)

    def __init__(self, options, initial_query='', make_complition=None):
        """
        options - a function that receives user input
                  and returns options to select from
        """
        super(Selector, self).__init__()
        self.keys = {
            1: self.move_caret_start,  # command + left
            5: self.move_caret_end,  # command + right
            9: self.complete,  # tab
            # 10: lambda: None,  # enter
            23: self.delete_word,  # alt + delete
            # 27: lambda: None,  # escape
            21: self.delete_to_start,  # command + delete
            # 98: self.move_caret_word_left,  # alt + left
            # 102: self.move_caret_word_right,  # alt + right
            127: self.deletech,  # delete
            263: self.deletech,  # delete
            258: self.move_selection_down,  # down
            259: self.move_selection_up,  # up
            260: self.move_caret_left,  # left arrow
            261: self.move_caret_right,  # right arrow
        }
        self.selected = 0
        self.shift_y = 0
        self.caret_x = len(initial_query)
        self.shift_x = 0
        self.width, self.height = get_terminal_size()
        self.height -= self.start_list_line
        self.chs = [ord(c) for c in initial_query]
        self.options = options
        self.items = []
        self.screen = curses.initscr()
        self.prev_word = None
        self.prev_length = 0
        self.make_complition = make_complition

    def setup(self, s):
        self.screen = s
        curses.noecho()
        curses.cbreak()
        curses.start_color()
        curses.use_default_colors()
        for i in range(0, curses.COLORS):
            curses.init_pair(i + 1, i, -1)
        self.screen.keypad(1)

    def cleanup(self):
        curses.nocbreak()
        self.screen.keypad(0)
        curses.echo()
        curses.endwin()

    def run(self):
        def f(s):
            self.setup(s)
            result = self.take_input()
            self.clear_list()
            return result
        result = curses.wrapper(f)
        self.cleanup()
        return result

    def take_input(self):
        while True:
            self.update()
            x = self.screen.getch()
            if x == self.ESCAPE:
                return self.empty_result
            elif x == self.ENTER:
                try:
                    item = self.items[self.selected]
                except IndexError:
                    item = None
                return Selection(
                    index=self.selected,
                    typed=self.chs_to_word(),
                    selected=item,
                    options=self.items
                )
            elif x in self.keys:
                self.keys[x]()
            else:
                self.addch(x)

    def chs_to_word(self):
        result = []
        for ch in self.chs:
            try:
                result.append(chr(ch))
            except ValueError:
                pass
        return ''.join(result)

    def update(self):
        search_color = curses.color_pair(self.COLOR_SEARCH_BOX)
        start = max(self.caret_x - self.width, 0)
        end = min(len(self.chs), start + self.width)
        for i, ch in enumerate(self.chs[start:end]):
            self.screen.addch(0, i, ch, search_color)
        for i in range(len(self.chs), self.width):
            self.screen.addch(0, i, self.SPACE)
        self.update_list()
        self.update_caret()
        self.screen.refresh()

    def update_caret(self):
        self.screen.move(0, min(max(self.caret_x, 0), self.width))

    def update_list(self):
        self.clear_list()
        word = self.chs_to_word()
        self.items = self.options(word)
        if (self.prev_word and word != self.prev_word) or self.prev_length != len(self.items):
            self.selected = 0
            self.shift_y = 0
        self.prev_length = len(self.items)
        self.print_list(
            item_transformator=lambda x: x[0:self.width],
            mark_selected=True
        )

    def clear_list(self):
        self.print_list(item_transformator=lambda x: " " * self.width)

    def print_list(
        self,
        item_transformator=lambda x: x,
        mark_selected=False
    ):
        line_y = self.start_list_line
        selected_style = curses.color_pair(self.COLOR_SELECTION)
        for line_no, item in enumerate(self.items[self.shift_y:self.shift_y + self.height]):
            line_is_selected = line_no == self.selected - self.shift_y and mark_selected
            style = selected_style if line_is_selected else curses.A_NORMAL
            self.safe_addstr(line_y, 0, item_transformator(item), style)
            line_y += 1

    def safe_addstr(self, y, x, s, style=None):
        try:
            if style:
                self.screen.addstr(y, x, s, style)
            else:
                self.screen.addstr(y, x, s)
        except:
            pass

    def addch(self, ch):
        self.chs.insert(self.caret_x, ch)
        self.move_caret_right()

    def deletech(self):
        if self.chs:
            self.chs.pop(self.caret_x - 1)
            self.move_caret_left()

    def delete_word(self):
        if self.chs:
            self.chs.pop(self.caret_x - 1)
            self.move_caret_left()
            while self.caret_x > 0 and self.chs[self.caret_x - 1] != self.SPACE:
                self.chs.pop(self.caret_x - 1)
                self.move_caret_left()

    def delete_to_start(self):
        self.chs = self.chs[self.caret_x:]
        self.caret_x = 0

    def complete(self):
        item = self.items[self.selected]
        if self.make_complition:
            item = self.make_complition(item, self.chs_to_word())
        self.chs = [ord(l) for l in str(item)]
        self.caret_x = len(self.chs)
        self.selected = 0

    def move_caret_right(self):
        self.caret_x = min(self.caret_x + 1, len(self.chs))

    def move_caret_left(self):
        self.caret_x = max(self.caret_x - 1, 0)

    def move_caret_start(self):
        self.caret_x = 0

    def move_caret_end(self):
        self.caret_x = len(self.chs)

    def move_caret_word_right(self):
        while self.caret_x < len(self.chs) and self.chs[self.caret_x] != self.SPACE:
            self.move_caret_right()

    def move_caret_word_left(self):
        while self.caret_x > 0 and self.chs[self.caret_x] != self.SPACE:
            self.move_caret_left()

    def move_selection_up(self):
        self.selected = max(0, self.selected - 1)
        if self.selected < self.shift_y:
            self.shift_y = self.selected

    def move_selection_down(self):
        self.selected = min(len(self.items) - 1, self.selected + 1)
        if self.selected - self.shift_y == self.height:
            self.shift_y += 1


def options_from_list(options):
    def m(w):
        return filter(options, w)
    return m


def options_by_appending_option(options, *args):
    def m(w):
        return options(w) + list(args)
    return m


def options_by_prepending_option(options, *args):
    def m(w):
        return list(args) + options(w)
    return m


def get_terminal_size():
    # Based on http://stackoverflow.com/questions/566746/how-to-get-console-window-width-in-python
    import os
    env = os.environ

    def ioctl_GWINSZ(fd):
        try:
            import fcntl
            import termios
            import struct
            cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
        except:
            return
        return cr
    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        cr = (env.get('LINES', 25), env.get('COLUMNS', 80))
    return int(cr[1]), int(cr[0])


if __name__ == "__main__":
    import sys
    import os
    import docopt
    import subprocess
    input_text = sys.stdin.read()
    if not input_text:
        sys.exit(0)

    old_out = sys.__stdout__
    old_in = sys.__stdin__
    old_err = sys.__stderr__
    sys.__stdout__ = sys.stdout = open('/dev/tty', 'w')
    sys.__stdin__ = sys.stdin = open('/dev/tty')
    os.dup2(sys.stdin.fileno(), 0)

    result = select(options_from_list(input_text.splitlines()))
    selected = result.selected

    sys.stdout.flush()
    sys.stderr.flush()
    sys.stdin.close()
    sys.stdout.close()
    sys.stderr.close()
    sys.__stdout__ = sys.stdout = old_out
    sys.__stdin__ = sys.stdin = old_in
    sys.__stderr__ = sys.stderr = old_err

    if not selected:
        sys.exit(0)

    def write_to_file(filepath, text):
        with open(filepath, 'w') as f:
            print(f.write(text + '\n'))
            print(text)

    def append_to_file(filepath, text):
        with open(filepath, 'a') as f:
            print(f.write(text + '\n'))

    def execute_command(command, selected):
        subprocess.call(command.replace('@', selected), shell=True)

    def execute_command_with_echo(command, selected):
        subprocess.call('echo "{}" | {}'.format(selected, command), shell=True)

    arguments = docopt.docopt(__doc__)
    if arguments['--file']:
        write_to_file(arguments['--file'], selected)
    if arguments['--append']:
        append_to_file(arguments['--append'], selected)
    if arguments['--command']:
        execute_command(arguments['--command'], selected)
    if arguments['--echo']:
        execute_command_with_echo(arguments['--echo'], selected)
    if not any(arguments.values()):
        print(selected)
