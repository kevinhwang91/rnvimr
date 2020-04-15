"""
Implement rnvimr's split action for neovim

"""

import os
from ranger.api.commands import Command
from ranger.core.loader import Loadable


# pylint: disable=invalid-name
def edit_this_file(fm, split=None, start_line=1):
    """
    Edit ranger target file with neovim.

    :param fm object: ranger fm
    :param split str: neovim split command
    :param start_line int: start line number
    """

    try:
        pick_enable = fm.client.vars['rnvimr_pick_enable']
    except KeyError:
        pick_enable = 0
    cmd = []
    if pick_enable:
        cmd.append('close')
    else:
        cmd.append('let cur_tab = nvim_get_current_tabpage()')
        cmd.append('let cur_win = nvim_get_current_win()')
        cmd.append('noautocmd wincmd p')
    if split:
        cmd.append('if bufname("%") != ""')
        cmd.append(split)
        cmd.append('endif')
    cmd.append('silent! edit +normal\\ {}zt {}'.format(start_line, fm.thisfile))

    if pick_enable:
        cmd.append('call rnvimr#rpc#enable_attach_file()')
    else:
        cmd.append('if cur_tab != nvim_get_current_tabpage()')
        cmd.append('noautocmd call nvim_win_close(cur_win, 0)')
        cmd.append('noautocmd call rnvimr#toggle()')
        cmd.append('else')
        cmd.append('noautocmd call nvim_set_current_win(cur_win)')
        cmd.append('endif')
        cmd.append('noautocmd startinsert')
        cmd.append('unlet cur_tab')
        cmd.append('unlet cur_win')

    fm.client.command('|'.join(cmd), async_=True)


class SplitAndEdit(Command):
    """
    A command of ranger to split and edit file.

    """

    def execute(self):
        action = ' '.join(self.args[1:])
        if not self.fm.thisfile.is_file or not action:
            return
        edit_this_file(self.fm, split=action)


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

        edit_this_file(self.fm, start_line=start)
        if pager.visible:
            self.fm.pager_close()
        return None

    def tab(self, tabnum):
        return self._tab_directory_content()


class AttachFile(Command):
    """
    A command of ranger to attach file.

    """

    def execute(self):
        try:
            line = int(self.arg(1))
        except ValueError:
            line = 1

        path = self.rest(2)

        if not path and self.fm.client:
            path = self.fm.client.command_output('echo expand("#:p")')

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

                if self.fm.thisfile.has_preview():
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
