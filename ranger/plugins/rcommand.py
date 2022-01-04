"""
Implement rnvimr's split action for neovim

"""

import os
from ranger.api.commands import Command
from ranger.core.loader import Loadable


class NvimEdit(Command):
    """
    A command of ranger to use neovim's command to edit file.

    """

    def execute(self):
        last_arg = self.args[-1]
        if last_arg.lower() in ('true', 'false'):
            picker_enabled = self.args.pop().lower() == 'true'
        else:
            picker_enabled = None
        action = ' '.join(self.args[1:])

        if not self.fm.thisfile.is_file or not action:
            return
        self.fm.client.rpc_edit([self.fm.thisfile], edit=action, picker=picker_enabled)


class JumpNvimCwd(Command):
    """
    A command of ranger to jump into the cwd of neovim.

    """

    def execute(self):
        path = None
        if self.fm.client:
            path = self.fm.client.get_cwd()
        self.fm.cd(path)


class EmitRangerCwd(Command):
    """
    A command of ranger to emit cwd of ranger to neovim.

    """

    def execute(self):
        if self.fm.client:
            self.fm.client.set_cwd(self.fm.thisdir.path)
            self.fm.client.notify("CWD has been changed to " + self.fm.thisdir.path)


class ClearImage(Command):

    """A command of ranger to clear image"""

    def execute(self):
        columns = self.fm.ui.browser.columns
        if len(columns) > 1:
            columns[-1].clear_image(force=True)


class AttachFile(Command):
    """
    A command of ranger to attach file.

    """

    resolve_macros = False

    def execute(self):
        path = self.rest(1)

        if not path and self.fm.client:
            path = self.fm.client.get_cb()

        if os.path.isdir(path):
            dirname = path
        elif os.path.isfile(path):
            self.fm.attached_file = path
            dirname = os.path.dirname(path)
        else:
            return

        if self.fm.thisdir.path == dirname or self.fm.enter_dir(dirname):
            if os.path.isfile(path):
                self.fm.thisdir.refilter()
                self.fm.thisdir.move_to_obj(path)

            descr = 'Redraw manually after attach event'
            loadable = Loadable(self.redraw_status(), descr)
            self.fm.loader.add(loadable, append=True)

    def redraw_status(self):
        """
        Redraw statusbar cause by generator of Dictionary

        """
        self.fm.ui.status.request_redraw()
        yield
