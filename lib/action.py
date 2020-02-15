"""
Implement rnvimr split action.
"""
from ranger.api.commands import Command
from .client import client


class SplitAndEdit(Command):
    """
    A plugin of ranger to split and edit file.
    """

    def execute(self):
        action = ' '.join(self.args[1:])
        if not self.fm.thisfile.is_file or not action:
            return
        try:
            pick_enable = client.vars['rnvimr_pick_enable']
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
            client.call('rnvimr#rpc#enable_attach_file', async_=True)

        client.command('|'.join(cmd), async_=True)
