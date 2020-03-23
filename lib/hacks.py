"""
Make ranger adjust to floating window of neovim

"""
import os
import inspect
import textwrap
import pynvim
import ranger


class Hacks():
    """
    Hacking ranger

    """

    def __init__(self, fm, hook_init):
        self.fm = fm  # pylint: disable=invalid-name
        self.fm.client = None
        self.fm.service = None
        self.fm.chan_id = None
        self.fm.attached_file = None
        self.commands = fm.commands
        self.old_hook_init = hook_init
        self.old_accept_file = ranger.container.directory.accept_file

    def hook_init(self):
        """
        Initialize via ranger hook_init.

        """

        self.bind_client()
        self.show_attached_file()
        self.map_split_action()
        self.calibrate_ueberzug()
        self.fix_editor()
        self.fix_quit()
        self.fix_bulkrename()
        return self.old_hook_init(self.fm)

    def bind_client(self):
        """
        Bind client of neovim.

        """

        socket_path = os.getenv('NVIM_LISTEN_ADDRESS')

        if socket_path:
            self.fm.client = pynvim.attach('socket', path=socket_path)

    def show_attached_file(self):
        """
        Always show attached file.

        """

        def accept_file(fobj, filters):
            if fobj.path == self.fm.attached_file:
                return True
            return self.old_accept_file(fobj, filters)

        ranger.container.directory.accept_file = accept_file

    def map_split_action(self):
        """
        Bind key for spliting action.

        """

        try:
            action_dict = self.fm.client.vars['rnvimr_split_action']
        except KeyError:
            return
        if not action_dict or not isinstance(action_dict, dict):
            return
        for key, val in action_dict.items():
            self.fm.execute_console('map {} SplitAndEdit {}'.format(key, val))

    def fix_editor(self):
        """
        Avoid to block and redraw ranger after opening editor, make rifle smarter.

        """

        self.fm.rifle.hook_before_executing = lambda command, mimetype, flags: \
            self.fm.ui.suspend() if 'f' not in flags and '$EDITOR' not in command else None
        self.fm.rifle.hook_after_executing = lambda command, mimetype, flags: \
            self.fm.ui.initialize() if 'f' not in flags and '$EDITOR' not in command else None

    def fix_quit(self):
        """
        Make ranger pretend to quit.

        """

        quit_cls = self.commands.get_command('quit')
        if not quit_cls:
            return

        def execute(self):

            if len(self.fm.tabs) >= 2:
                self.fm.tab_close()
            else:
                self.fm.client.call('rnvimr#rpc#enable_attach_file', async_=True)
                self.fm.client.request('nvim_win_close', 0, 1, async_=True)

        quit_cls.execute = execute

    def fix_bulkrename(self):
        """
        Bulkrename need a block workflow, so restore the raw editor to edit file name.
        To avoid maintaining code about bulkrename, hack code to replace label for rifle.

        """

        bulkrename_cls = self.commands.get_command('bulkrename')
        if not bulkrename_cls:
            return

        editor = os.getenv('EDITOR')
        if not editor:
            editor = 'nvim'
        code = textwrap.dedent(inspect.getsource(bulkrename_cls.execute))
        code = code.replace('def execute', 'def bulkrename_execute')
        code = code.replace("app='editor'", "app='{}'".format(editor))

        bulkrename_module = inspect.getmodule(bulkrename_cls)
        exec(code, bulkrename_module.__dict__)  # pylint: disable=exec-used

        bulkrename_cls.execute = bulkrename_module.bulkrename_execute

    def calibrate_ueberzug(self):
        """
        Ueberzug can't capture the calibration of floating window of neovim, fix it.

        """

        client = self.fm.client

        def wrap_draw(self, path, start_x, start_y, width, height):
            win_info = client.request('nvim_win_get_config', 0)
            if not win_info['relative']:
                return
            start_x += win_info['col']
            start_y += win_info['row']

            self.raw_draw(path, start_x, start_y, width, height)

        try:
            # ueberzug is supported by ranger since [b58954d4258bc204c38f635e5209e6c1e2bce743]
            # https://github.com/ranger/ranger/commit/b58954d4258bc204c38f635e5209e6c1e2bce743
            # pylint: disable=import-outside-toplevel
            from ranger.ext.img_display import UeberzugImageDisplayer
        except ImportError:
            pass
        else:
            UeberzugImageDisplayer.raw_draw = UeberzugImageDisplayer.draw
            UeberzugImageDisplayer.draw = wrap_draw


OLD_HOOK_INIT = ranger.api.hook_init
ranger.api.hook_init = lambda fm: Hacks(fm, OLD_HOOK_INIT).hook_init()
