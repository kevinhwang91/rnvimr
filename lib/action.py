"""
Implement rnvimr's split action for neovim

"""

import os
from ranger.api.commands import Command
from ranger.core.loader import Loadable


def edit_this_file(fm, split=None, start_line=1):
# pylint: disable=invalid-name
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
        if not pager.visible:
            arg1 = self.arg(1)
            arg2 = self.arg(2)
            return self.fm.edit_file(arg2) if arg1 == 'file' else self.fm.edit_file(arg1)

        start = pager.scroll_begin + 1
        edit_this_file(self.fm, start_line=start)
        self.fm.pager_close()
        return


class AttachFile(Command):
    """
    A command of ranger to attach file.

    """

    def execute(self):
        path = self.arg(1)

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

            descr = 'Redraw manually after attach event'
            loadable = Loadable(self.redraw_status(), descr)
            self.fm.loader.add(loadable, append=True)

    def redraw_status(self):
        """
        Redraw statusbar cause by generator of Dictionary

        """
        self.fm.ui.status.request_redraw()
        yield
