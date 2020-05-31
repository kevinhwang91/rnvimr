"""
Make ranger as a client to neovim

"""
import os
import pynvim


class Client():
    """
    Ranger client for RPC

    """

    def __init__(self):
        self.nvim = None

    def attach_nvim(self):
        """
        Attach neovim session by socket path.

        """
        socket_path = os.getenv('NVIM_LISTEN_ADDRESS')

        if socket_path:
            self.nvim = pynvim.attach('socket', path=socket_path)

    def hide_window(self):
        """
        Hide the floating window.

        """
        self.nvim.call('rnvimr#rpc#enable_attach_file', async_=True)
        self.nvim.request('nvim_win_close', 0, 1, async_=True)

    def set_winhl(self, winhl):
        """
        Set the floating window highlight.

        :param winhl str: variable in ranger buffer
        """
        self.nvim.call('rnvimr#rpc#set_winhl', winhl)

    def get_cb(self):
        """
        Get current buffer of neovim.

        """
        return self.nvim.command_output('echo expand("#:p")')

    def get_cwd(self):
        """
        Get current work directory of neovim.

        """
        return self.nvim.command_output('pwd')

    def set_cwd(self, path):
        """
        Set current work directory of neovim.

        """
        self.nvim.command('cd {}'.format(path))

    def rpc_edit(self, files, edit=None, start_line=0):
        """
        Edit ranger target files in neovim though RPC.

        :param files list: list of file name
        :param edit str: neovim edit command
        :param start_line int: start line number
        """

        if not files:
            return

        try:
            pick_enable = self.nvim.vars['rnvimr_pick_enable']
        except KeyError:
            pick_enable = 0
        cmd = []
        if pick_enable:
            cmd.append('close')
        else:
            cmd.append('let rnvimr_cur_tab = nvim_get_current_tabpage()')
            cmd.append('let rnvimr_cur_win = nvim_get_current_win()')
            cmd.append('wincmd p')
        if edit:
            cmd.append('if bufname("%") != ""')
            cmd.append(edit)
            cmd.append('endif')
            cmd.append('silent! edit {}'.format(files[0]))
        else:
            if start_line == 0:
                cmd.append('silent! arglocal {}'.format(' '.join(files)))
                cmd.append('argglobal')
            else:
                cmd.append('silent! edit +normal\\ {}zt {}'.format(start_line, files[0]))

        if pick_enable:
            cmd.append('call rnvimr#rpc#enable_attach_file()')
        else:
            cmd.append('call rnvimr#rpc#buf_checkpoint()')
            cmd.append('if rnvimr_cur_tab != nvim_get_current_tabpage()')
            cmd.append('noautocmd call nvim_win_close(rnvimr_cur_win, 0)')
            cmd.append('call rnvimr#toggle()')
            cmd.append('else')
            cmd.append('call nvim_set_current_win(rnvimr_cur_win)')
            cmd.append('endif')
            cmd.append('noautocmd startinsert')
            cmd.append('unlet rnvimr_cur_tab')
            cmd.append('unlet rnvimr_cur_win')

        cmd.append('cd .')
        self.nvim.command('|'.join(cmd), async_=True)
