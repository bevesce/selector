# I'm trying how to figure out how to make
# `echo $(ls | python3 selector.py)` work

import os, sys
import curses


old_out = sys.__stdout__
old_in = sys.__stdin__
old_err = sys.__stderr__
sys.__stdout__ = sys.stdout = open('/dev/tty', 'w')
sys.__stdin__ = sys.stdin = open('/dev/tty')
sys.__stderr__ = sys.stderr = open('/dev/tty')

def show_a(s):
    s.addch(ord('a'))
    print(s.getch())

curses.wrapper(show_a)

sys.stdin.flush()
sys.stdout.flush()
sys.stderr.flush()
sys.stdin.close()
sys.stdout.close()
sys.stderr.close()
sys.__stdout__ = sys.stdout = old_out
sys.__stdin__ = sys.stdin = old_in
sys.__stderr__ = sys.stderr = old_err
print('yo')