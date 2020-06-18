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

    def get_window_info(self):
        """
        Get the floating window info.

        """
        return self.nvim.request('nvim_win_get_config', 0)

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

        self.nvim.call('rnvimr#rpc#edit', edit, start_line,
                       [str(file) for file in files], async_=True)
