"""
util

"""

import os

def find_git_root(path):
    """
    find a git root directory

    :param path str: absolute path
    """
    while True:
        if os.path.basename(path) == '.git':
            return None
        repodir = os.path.join(path, '.git')
        if os.path.exists(repodir):
            return path
        path_o = path
        path = os.path.dirname(path)
        if path == path_o:
            return None
