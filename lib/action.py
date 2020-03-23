"""
Implement rnvimr's split action for neovim

"""

import os
from ranger.api.commands import Command
from ranger.core.loader import Loadable


class SplitAndEdit(Command):
    """
    A command of ranger to split and edit file.

    """

    def execute(self):
        action = ' '.join(self.args[1:])
        if not self.fm.thisfile.is_file or not action:
            return
        try:
            pick_enable = self.fm.client.vars['rnvimr_pick_enable']
        except KeyError:
            pick_enable = 0
        cmd = []
        if pick_enable:
            cmd.append('close')
        else:
            cmd.append('let cur_win = nvim_get_current_win()')
            cmd.append('noautocmd wincmd p')
        cmd.append('if bufname("%") != ""')
        cmd.append(action)
        cmd.append('endif')
        cmd.append('silent! edit {}'.format(self.fm.thisfile))

        if not pick_enable:
            cmd.append('noautocmd call nvim_set_current_win(cur_win)')
            cmd.append('noautocmd startinsert')
        else:
            self.fm.client.call('rnvimr#rpc#enable_attach_file', async_=True)

        self.fm.client.command('|'.join(cmd), async_=True)


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
