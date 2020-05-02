"""
Make ranger adjust to floating window of neovim

"""
import os
import inspect
import textwrap
import pynvim
import ranger
from ranger.gui.ui import UI


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
        self.fix_pager()
        self.fix_vcs()
        self.draw_border()
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
            return old_accept_file(fobj, filters)

        old_accept_file = ranger.container.directory.accept_file
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

        #  Make sure editor's path of pynvim the same with ranger's.
        site_package = os.path.dirname(os.path.dirname(inspect.getfile(pynvim)))
        python_path = os.getenv('PYTHONPATH')
        os.environ['PYTHONPATH'] = site_package if not python_path \
            else '{}:{}'.format(python_path, site_package)

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

    def fix_pager(self):
        """
        Synchronize scroll line of pager in ranger with line number in neovim.

        """

        if not self.commands.get_command('EditFile'):
            return

        self.commands.alias('edit_file', 'EditFile')
        self.commands.alias('edit', 'EditFile')
        raw_open_pager = UI.open_pager
        raw_close_pager = UI.close_pager

        def wrap_open_pager(self):
            pager = raw_open_pager(self)
            pager.scroll_begin = self.browser.columns[-1].scroll_extra
            return pager

        def wrap_close_pager(self):
            self.browser.columns[-1].scroll_extra = self.pager.scroll_begin
            raw_close_pager(self)

        UI.open_pager = wrap_open_pager
        UI.close_pager = wrap_close_pager

    def fix_vcs(self):
        """
        Vcs in ranger is a bad design. It will produce a death lock with
        --cmd='set column_ratios 1,1' caused by 'ui.redraw'.

        """

        def enable_vcs_aware():
            """
            Use a queue loader to enable vcs_aware to avoid a death lock.

            """
            self.fm.execute_console('set vcs_aware True')
            self.fm.thisdir.load_content(schedule=False)
            yield

        if self.fm.settings.vcs_aware:
            # pylint: disable=import-outside-toplevel
            from ranger.core.loader import Loadable
            self.fm.execute_console('set vcs_aware False')
            descr = "Restore user's setting of vcs_aware"
            loadable = Loadable(enable_vcs_aware(), descr)
            self.fm.loader.add(loadable)

    def calibrate_ueberzug(self):
        """
        Ueberzug can't capture the calibration of floating window of neovim, fix it.

        """

        client = self.fm.client

        # pylint: disable=too-many-arguments
        def wrap_draw(self, path, start_x, start_y, width, height):
            win_info = client.request('nvim_win_get_config', 0)
            if not win_info['relative']:
                return
            start_x += win_info['col']
            start_y += win_info['row']

            raw_draw(self, path, start_x, start_y, width, height)

        try:
            # ueberzug is supported by ranger since [b58954d4258bc204c38f635e5209e6c1e2bce743]
            # https://github.com/ranger/ranger/commit/b58954d4258bc204c38f635e5209e6c1e2bce743
            # pylint: disable=import-outside-toplevel
            from ranger.ext.img_display import UeberzugImageDisplayer
        except ImportError:
            pass
        else:
            raw_draw = UeberzugImageDisplayer.draw
            UeberzugImageDisplayer.draw = wrap_draw

    def draw_border(self):
        """
        Using curses draw a border of floating window.

        """

        try:
            draw_border = self.fm.client.vars['rnvimr_draw_border']
            if not draw_border:
                return
        except KeyError:
            return

        def update_size(self):
            self.termsize = self.win.getmaxyx()
            y, x = self.termsize  # pylint: disable=invalid-name
            y, x = y - 2, x - 2  # pylint: disable=invalid-name
            self.browser.resize(self.settings.status_bar_on_top and 3 or 2, 1, y - 2, x)
            self.taskview.resize(2, 1, y - 2, x)
            self.pager.resize(2, 1, y - 2, x)
            self.titlebar.resize(1, 1, 1, x)
            self.status.resize(self.settings.status_bar_on_top and 2 or y, 1, 1, x)
            self.console.resize(y, 1, 1, x)

        UI.update_size = update_size

        import curses  # pylint: disable=import-outside-toplevel

        def wrap_draw(self):
            self.win.border(curses.ACS_VLINE, curses.ACS_VLINE, curses.ACS_HLINE,
                            curses.ACS_HLINE, curses.ACS_ULCORNER, curses.ACS_URCORNER,
                            curses.ACS_LLCORNER, curses.ACS_LRCORNER)
            raw_draw(self)

        raw_draw = UI.draw
        UI.draw = wrap_draw

        def wrap_initialize(self):
            self.fm.client.command(
                'call setwinvar(0, "&winhighlight", getbufvar(0, "curses_winhl"))')
            raw_initialize(self)

        raw_initialize = UI.initialize
        UI.initialize = wrap_initialize

        def wrap_suspend(self):

            def check_destory():
                for displayable in self.container:
                    if displayable.win:
                        if hasattr(displayable, 'container'):
                            for child in displayable.container:
                                if child.win:
                                    return False
                        else:
                            return False
                return True

            raw_suspend(self)
            #  destory don't restore the NormalFloat highlight
            if not check_destory():
                self.fm.client.command('call setwinvar(0, "&winhighlight", "")')

        raw_suspend = UI.suspend
        UI.suspend = wrap_suspend


OLD_HOOK_INIT = ranger.api.hook_init
ranger.api.hook_init = lambda fm: Hacks(fm, OLD_HOOK_INIT).hook_init()
