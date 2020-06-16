"""
Make ranger adjust to floating window of neovim

"""
import os
import inspect
import textwrap
import curses
import ranger
from ranger.ext.rifle import Rifle
from ranger.gui.ui import UI
from ranger.core.loader import Loadable
from .client import Client


class Hacks():
    """
    Hacking ranger

    """

    def __init__(self, fm, hook_init):
        self.fm = fm  # pylint: disable=invalid-name
        self.fm.client = None
        self.fm.service = None
        self.fm.attached_file = None
        self.commands = fm.commands
        self.old_hook_init = hook_init

    def hook_init(self):
        """
        Initialize via ranger hook_init.

        """

        self.client_attach()
        self.show_attached_file()
        self.map_action()
        self.calibrate_ueberzug()
        self.fix_editor()
        self.fix_quit()
        self.fix_bulkrename()
        self.fix_pager()
        self.fix_column_ratio()
        self.fix_vcs()
        self.draw_border()
        return self.old_hook_init(self.fm)

    def client_attach(self):
        """
        Client attach  neovim.

        """

        self.fm.client = Client()
        self.fm.client.attach_nvim()

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

    def map_action(self):
        """
        Bind key for action.

        """

        try:
            action_dict = self.fm.client.nvim.vars['rnvimr_action']
        except KeyError:
            return
        if not action_dict or not isinstance(action_dict, dict):
            return
        for key, val in action_dict.items():
            self.fm.execute_console('map {} {}'.format(key, val))

    def fix_editor(self):
        """
        Avoid to block and redraw ranger after opening editor, make rifle smarter.
        Use a 'true' built-in command to mock a dummy $EDITOR.
        """

        client = self.fm.client

        def wrap_build_command(self, files, action, flags):
            if '$EDITOR' in action:
                client.rpc_edit(files)
                self._app_flags = 'f'
                return 'true'
            return raw_build_command(self, files, action, flags)

        raw_build_command = Rifle._build_command  # pylint: disable=protected-access
        Rifle._build_command = wrap_build_command  # pylint: disable=protected-access

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
                self.fm.client.hide_window()

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

    def fix_column_ratio(self):
        """
        set column_ratios will reconstruct Browser widget.
        Browser widget referenced by Status widget can't be updated.

        """

        def sync_status():
            self.fm.ui.status.column = self.fm.ui.browser.main_column

        self.fm.settings.signal_bind('setopt.column_ratios', sync_status, priority=0.05)

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
            self.fm.execute_console('set vcs_aware False')
            descr = "Restore user's setting of vcs_aware"
            loadable = Loadable(enable_vcs_aware(), descr)
            self.fm.loader.add(loadable)

    def calibrate_ueberzug(self):
        """
        Ueberzug can't capture the calibration of floating window of neovim, fix it.

        """

        nvim = self.fm.client.nvim
        # pylint: disable=too-many-arguments

        def wrap_draw(self, path, start_x, start_y, width, height):
            win_info = nvim.request('nvim_win_get_config', 0)
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

    def fix_ui(self, attr, client):
        """
        Call by draw_border, fix UI to draw a border.

        :param attr int: attribute of curses
        :param client object: Object of attached neovim session
        """
        def update_size(self):
            self.win.erase()
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

        def wrap_draw(self):
            self.win.attrset(attr)
            self.win.border(curses.ACS_VLINE, curses.ACS_VLINE, curses.ACS_HLINE,
                            curses.ACS_HLINE, curses.ACS_ULCORNER, curses.ACS_URCORNER,
                            curses.ACS_LLCORNER, curses.ACS_LRCORNER)
            raw_draw(self)

        raw_draw = UI.draw
        UI.draw = wrap_draw

        def wrap_initialize(self):
            client.set_winhl('curses_winhl')
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
                client.set_winhl('normal_winhl')

        raw_suspend = UI.suspend
        UI.suspend = wrap_suspend

    def fix_view_miller(self, attr):
        """
        Call by draw_border, fix ViewMiller can't draw border properly.

        :param attr int: attribute of curses
        """
        # pylint: disable=import-outside-toplevel
        from ranger.gui.widgets.view_miller import ViewMiller

        code = textwrap.dedent(inspect.getsource(ViewMiller.resize))
        code = code.replace('def resize', 'def view_miller_resize')
        code = code.replace('left = pad', 'left = 0')
        code = code.replace('wid = int(self.wid - left + 1 - pad)',
                            'wid = int(self.wid - left + 1)')

        view_miller_module = inspect.getmodule(ViewMiller)
        exec(code, view_miller_module.__dict__)  # pylint: disable=exec-used

        ViewMiller.resize = view_miller_module.view_miller_resize

        def view_miller_draw_border(self, border_types):
            self.win.attrset(attr)
            if 'outline' in border_types:
                try:
                    self.win.hline(0, 0, curses.ACS_HLINE, self.wid)
                    self.win.hline(self.hei - 1, 0, curses.ACS_HLINE, self.wid)
                    y, x = self.win.getparyx()  # pylint: disable=invalid-name
                    self.parent.addch(y, 0, curses.ACS_LTEE)
                    self.parent.addch(y, self.wid + 1, curses.ACS_RTEE)
                    self.parent.addch(y + self.hei - 1, 0, curses.ACS_LTEE)
                    self.parent.addch(y + self.hei - 1, self.wid + 1, curses.ACS_RTEE)
                except curses.error:
                    pass

            if 'separators' in border_types:
                for child in self.columns[:-1]:
                    if not child.has_preview():
                        continue
                    if child.main_column and self.pager.visible:
                        break
                    y, x = self.hei - 1, child.x + child.wid - 1  # pylint: disable=invalid-name
                    try:
                        self.win.vline(1, x, curses.ACS_VLINE, y - 1)
                        if 'outline' in border_types:
                            self.addch(0, x, curses.ACS_TTEE, 0)
                            self.addch(y, x, curses.ACS_BTEE, 0)
                        else:
                            self.addch(0, x, curses.ACS_VLINE, 0)
                            self.addch(y, x, curses.ACS_VLINE, 0)
                    except curses.error:
                        pass

        ViewMiller._draw_borders = view_miller_draw_border  # pylint: disable=protected-access

    def draw_border(self):
        """
        Using curses draw a border of floating window.

        """

        client = self.fm.client
        try:
            draw_border = client.nvim.vars['rnvimr_draw_border']
        except KeyError:
            return
        if not draw_border:
            return

        from ranger.gui import color  # pylint: disable=import-outside-toplevel

        try:
            attr_dict = client.nvim.vars['rnvimr_border_attr']
        except KeyError:
            attr_dict = {}

        try:
            attr_fg, attr_bg = attr_dict.get('fg', -1), attr_dict.get('bg', -1)
            attr_fg, attr_bg = int(attr_fg), int(attr_bg)
            if not -1 <= attr_fg < 256:
                attr_fg = -1
            if not -1 <= attr_bg < 256:
                attr_bg = -1
        except TypeError:
            attr_fg, attr_bg = -1, -1
        except ValueError:
            attr_fg, attr_bg = -1, -1

        attr = curses.color_pair(color.get_color(attr_fg, attr_bg))

        self.fix_ui(attr, client)
        self.fix_view_miller(attr)


OLD_HOOK_INIT = ranger.api.hook_init
ranger.api.hook_init = lambda fm: Hacks(fm, OLD_HOOK_INIT).hook_init()
