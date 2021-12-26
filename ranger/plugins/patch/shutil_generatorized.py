"""
Patch ranger.ext.shutil_generatorized

"""
import os
from shutil import _basename
from ranger.ext import shutil_generatorized
from ranger.ext.safe_path import get_safe_path


def wrap_move(client):
    """
    CopyLoader with do_cut parameter will invoke this method.
    Wrap low-level move method to save information in loaded buffers.

    :param client object: Object of attached neovim session
    """
    def move(src, dst, overwrite, make_safe_path=get_safe_path):

        real_dst = os.path.join(dst, _basename(src))
        if not overwrite:
            real_dst = make_safe_path(real_dst)
        yield from raw_move(src, dst, overwrite, make_safe_path)
        client.move_buf(src, real_dst)

    raw_move = shutil_generatorized.move
    shutil_generatorized.move = move
