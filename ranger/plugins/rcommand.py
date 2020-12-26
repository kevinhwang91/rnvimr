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
        action = ' '.join(self.args[1:])
        if not self.fm.thisfile.is_file or not action:
            return
        self.fm.client.rpc_edit([self.fm.thisfile], edit=action)


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

class EditFile(Command):
    """
    A command of ranger to wrap native 'edit_file' for pager.

    """

    def execute(self):
        pager = self.fm.ui.pager
        if self.arg(1):
            return self.fm.edit_file(self.arg(1))

        if pager.visible:
            start = pager.scroll_begin + 1
        elif self.fm.thisfile.has_preview():
            start = self.fm.ui.browser.columns[-1].scroll_extra + 1
        else:
            start = 1

        self.fm.client.rpc_edit([self.fm.thisfile], start_line=start)
        if pager.visible:
            self.fm.pager_close()
        return None

    def tab(self, tabnum):
        return self._tab_directory_content()

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
        try:
            line = int(self.arg(1))
        except ValueError:
            line = 1

        path = self.rest(2)

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

                if hasattr(self.fm.thisfile, 'has_preview') and self.fm.thisfile.has_preview():
                    descr = 'Scroll the line for preview file'
                    loadable = Loadable(self.scroll_preview(line - 1), descr)
                    self.fm.loader.add(loadable, append=True)

            descr = 'Redraw manually after attach event'
            loadable = Loadable(self.redraw_status(), descr)
            self.fm.loader.add(loadable, append=True)

    def scroll_preview(self, line):
        """
        scroll the line for preview column

        :param line int: scroll the line for preview column
        """
        self.fm.ui.browser.columns[-1].scroll_extra = 0
        self.fm.scroll_preview(line)
        yield

    def redraw_status(self):
        """
        Redraw statusbar cause by generator of Dictionary

        """
        self.fm.ui.status.request_redraw()
        yield
