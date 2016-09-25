import os
import subprocess

from selector import select, options_from_list, options_by_appending_option

DEFAULT_EXTENSION = '.md'


def find_and_open_note(dirpath):
    filenames = [x for x in os.listdir(dirpath) if not x.startswith('.')]
    result = select(
        options_by_appending_option(
            options_from_list(filenames),
            '+ create'
        )
    )
    if not result.selected:
        return
    selected_create_new_note = len(result.options) == 1
    if selected_create_new_note:
        filename = result.typed
        if '.' not in filename:
            filename += DEFAULT_EXTENSION
    else:
        filename = result.selected
    subprocess.call(
        ['vim', os.path.join(dirpath, filename)]
    )


if __name__ == '__main__':
    find_and_open_note(os.path.expanduser('~/Dropbox/Notes/'))
