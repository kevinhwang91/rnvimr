"""
util

"""

import os
import sys
from importlib import util
import pynvim


def attach_nvim(server_name):
    """
    A wrapper of Pynvim attach

    :param server_name str: server_name, maybe socket or tcp
    """

    nvim = None
    if server_name:
        try:
            nvim = pynvim.attach('socket', path=server_name)
        except FileNotFoundError:
            try:
                addr, port = server_name.split(':')
                nvim = pynvim.attach('tcp', address=addr, port=port)
            except ValueError:
                pass
    return nvim


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


def is_subpath(spath, lpath):
    """
    check the short path is a subpath of long path

    :param spath str: short path
    :param lpath str: long path
    """

    if lpath.startswith(spath):
        slen, llen = len(spath), len(lpath)
        return True if slen == llen else lpath[slen] == '/'
    return False


def dynamic_import(name, path):
    """
    import single moudle dynamically

    :param name str: module name
    :param path str: module path
    """
    if name in sys.modules:
        return None

    spec = util.spec_from_file_location(name, path)
    module = util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module
