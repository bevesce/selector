from selector import select, make_fuzzy_matcher_from_list, append_msg
import os
import sys
import subprocess

dirpath = os.path.expanduser('~/Dropbox/Notes/')
default_extension = '.md'

l = os.listdir(dirpath)
l = [x for x in l if not x.startswith('.')]
msg = '+ create'
_, typed, selected = select(
    append_msg(
        make_fuzzy_matcher_from_list(l),
        msg
    )
)
if not selected:
    sys.exit(0)

filename = selected
if msg == selected:
    filename = typed
    if '.' not in filename:
        filename += default_extension
    open(os.path.join(dirpath, filename), 'a').close()
subprocess.call(
    'subl "{}"'.format(os.path.join(dirpath, filename)),
    shell=True,
)
