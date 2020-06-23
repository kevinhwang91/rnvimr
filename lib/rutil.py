"""
util

"""

import os
from pathlib import Path

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

def is_path_subset(spath, lpath):
    """
    check the short path is a subset of long path

    :param spath str: short path
    :param lpath str: long path
    """
    return Path(spath) in Path(lpath).parents or Path(spath) == Path(lpath)
