"""
Make ranger adjust to floating window of neovim

"""
import curses
import ranger
from ranger.core.loader import Loadable
from . import rifle
from . import ueberzug
from . import ui
from . import viewmiller
from . import action
from . import directory
from . import ccommands
from . import shutil_generatorized
from .client import Client
from .urc import load_user_settings


class Hacks():
    """
    Hacking ranger

    """

    def __init__(self, fm, hook_init):
        self.fm = fm  # pylint: disable=invalid-name
        self.fm.client = None
        self.fm.service = None
        self.fm.attached_file = None
        self.old_hook_init = hook_init

    def hook_init(self):
        """
        Initialize via ranger hook_init.

        """

        self.client_attach()
        self.map_action()
        self.fake_editor()
        self.hide_git_files()
        self.show_attached_file()
        self.load_user_settings()
        self.draw_border()
        self.change_view_adapt_size()
        self.calibrate_ueberzug()
        self.enhance_move_file()
        self.enhance_scroll_pager()
        self.enhance_quit()
        self.fix_column_ratio()
        self.fix_vcs()
        return self.old_hook_init(self.fm)

    def client_attach(self):
        """
        Client attach neovim.

        """

        self.fm.client = Client()
        self.fm.client.attach_nvim()

    def map_action(self):
        """
        Bind key for action.

        """

        try:
            action_dict = self.fm.client.nvim.vars['rnvimr_action']
        except KeyError:
            action_dict = None
        if not action_dict or not isinstance(action_dict, dict):
            return
        for key, val in action_dict.items():
            self.fm.execute_console('map {} {}'.format(key, val))

    def fake_editor(self):
        """
        Avoid to block and redraw ranger after opening editor, make rifle smarter.
        Use a 'true' built-in command to mock a dummy $EDITOR.
        """

        rifle.build_fake_editor(self.fm.client)

    def hide_git_files(self):
        """
        Hide the files included in gitignore.

        """

        client = self.fm.client
        try:
            hide_git = client.nvim.vars['rnvimr_hide_gitignore']
        except KeyError:
            hide_git = None
        if not hide_git:
            return

        directory.wrap_dir_for_git()

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

    def load_user_settings(self):
        """
        Load user settings.

        """

        client = self.fm.client
        try:
            vanilla = client.nvim.vars['rnvimr_vanilla']
        except KeyError:
            vanilla = None
        if vanilla:
            return

        try:
            user_rc_path = client.nvim.vars['rnvimr_urc_path']
        except KeyError:
            user_rc_path = None

        ranger.api.hook_init = self.old_hook_init
        load_user_settings(self.fm, user_rc_path)
        self.old_hook_init = ranger.api.hook_init

    def draw_border(self):
        """
        Using curses draw a border of floating window.

        """

        client = self.fm.client
        try:
            draw_border = client.nvim.vars['rnvimr_draw_border']
        except KeyError:
            draw_border = None
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

        ui.enhance_draw_border(attr, client)
        viewmiller.enhance_draw_border(attr)

    def change_view_adapt_size(self):
        """
        Ranger change view to adapt size of the floating window.

        """
        client = self.fm.client
        try:
            views = client.nvim.vars['rnvimr_ranger_views']
        except KeyError:
            views = None
        if not views or not isinstance(views, list):
            return

        column_ratios = self.fm.settings['column_ratios']
        for view in views:
            if not isinstance(view, dict):
                return
            min_width = view.setdefault('minwidth', 0)
            max_width = view.setdefault('maxwidth', 1023)
            ratio = view['ratio']
            if not ratio:
                ratio = view['ratio'] = column_ratios
            if min_width > max_width or not isinstance(ratio, list):
                return
            column_size = len(ratio)
            if column_size == 1:
                view['viewmode'] = 'multipane'
            elif column_size > 1:
                view['viewmode'] = 'miller'
        ui.wrap_update_size(views)

    def calibrate_ueberzug(self):
        """
        Ueberzug can't capture the calibration of floating window of neovim, fix it.

        """
        ueberzug.wrap_draw(self.fm.client)

    def enhance_move_file(self):
        """
        Persistent information of loaded buffers will be copied to destination files moved
        by ranger and neovim will load destination files as buffers automatically.

        """
        action.enhance_rename(self.fm.client)
        shutil_generatorized.wrap_move(self.fm.client)
        ccommands.enhance_bulkrename(self.fm.commands, self.fm.client)

    def enhance_scroll_pager(self):
        """
        Synchronize scroll line of pager in ranger with line number in neovim.

        """
        ccommands.alias_edit_file(self.fm.commands)
        ui.wrap_pager()

    def enhance_quit(self):
        """
        Make ranger pretend to quit.

        """
        ccommands.enhance_quit(self.fm.commands, self.fm.client)

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
            self.fm.execute_console('set vcs_aware False')
            descr = "Restore user's setting of vcs_aware"
            loadable = Loadable(enable_vcs_aware(), descr)
            self.fm.loader.add(loadable)


OLD_HOOK_INIT = ranger.api.hook_init
ranger.api.hook_init = lambda fm: Hacks(fm, OLD_HOOK_INIT).hook_init()
