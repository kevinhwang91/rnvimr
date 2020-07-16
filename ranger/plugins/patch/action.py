"""
Patch ranger.core.actions.Actions

"""

import os
from ranger.core.actions import Actions

def enhance_rename(client):
    """
    Enhance low-level rename method to save information in loaded buffers.

    :param client object: Object of attached neovim session
    """
    def rename(self, src, dest):
        if hasattr(src, 'path'):
            src = src.path

        try:
            os.makedirs(os.path.dirname(dest))
        except OSError:
            pass
        try:
            os.rename(src, dest)
        except OSError as err:
            self.notify(err)
            return False
        else:
            dst = os.path.abspath(dest)
            client.move_buf(src, dst)
        return True

    Actions.rename = rename
