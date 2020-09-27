"""
Make ranger as a client to neovim

"""
import os
import pynvim
from . import rutil


class Client():
    """
    Ranger client for RPC

    """

    def __init__(self):
        self.nvim = None

    def echom(self, msg):
        """
        Echo message.

        :param msg str: message be sent.
        """
        self.nvim.command('echom "{}"'.format(msg))

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
        return self.nvim.call('rnvimr#rpc#get_window_info')

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
        self.nvim.call('rnvimr#rpc#set_winhl', winhl, async_=True)

    def list_buf_name_nr(self):
        """
        List buffers in a dict, with name as key and number as val.

        """
        return self.nvim.call('rnvimr#rpc#list_buf_name_nr')

    def do_saveas(self, bufnr, target_name):
        """
        Use bufnr to save buffer as target_name.
        target_name must be existed before saving buffer, otherwise nothing happens.

        :param bufnr int: buffer number in neovim
        :param target_name str: absolute path of a target name
        """
        if not os.path.exists(target_name):
            return
        self.nvim.call('rnvimr#rpc#do_saveas', bufnr, target_name, async_=True)

    def move_buf(self, src, dst):
        """
        Move the buffer from src to dst for saving information of loaded buffers included in src.

        :param src str: absolute path of source
        :param dst str: absolute path of destination
        """
        buf_name_nr = self.list_buf_name_nr()
        isdir = os.path.isdir(dst)
        if isdir:
            ncwd = self.get_cwd()
            self.set_cwd('', noautocmd=True)
        for name, num in buf_name_nr.items():
            if isdir:
                if rutil.is_subpath(src, name):
                    real_dst = os.path.join(dst, os.path.relpath(name, src))
                    self.do_saveas(num, real_dst)
            elif name == src:
                self.do_saveas(num, dst)
                break

        if isdir:
            self.set_cwd(ncwd, noautocmd=True)

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

    def set_cwd(self, path, noautocmd=False):
        """
        Set current work directory of neovim.

        :param path str: absolute path
        :param noautocmd bool: whether use noautocmd command
        """
        self.nvim.command('{} cd {}'.format('noautocmd' if noautocmd else '', path))

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
