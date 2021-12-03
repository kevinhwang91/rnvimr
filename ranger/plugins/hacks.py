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
from .urc import Urc


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
        Get Neovim global vars at once to improve performance.

        """

        self.client_attach()
        try:
            init_dict = self.fm.client.nvim.vars['rnvimr_ranger_init']
        except KeyError:
            init_dict = {}
        self.fake_editor()
        self.hide_git_files(bool(init_dict.get('hide_gitignore')))
        self.map_action(init_dict.get('action'))
        self.draw_border(bool(init_dict.get('draw_border')), init_dict.get('border_attr'))
        self.change_view_adapt_size(init_dict.get('views'))
        self.calibrate_ueberzug()
        self.enhance_move_file()
        self.enhance_scroll_pager()
        self.enhance_quit()
        self.fix_column_ratio()
        self.fix_vcs()
        self.kill_redundant_redraw()
        return self.old_hook_init(self.fm)

    def client_attach(self):
        """
        Client attach neovim.

        """

        self.fm.client = Client()
        self.fm.client.attach_nvim()

    def map_action(self, action_dict):
        """
        Bind key for action in Ranger.

        :param action_dict dict: actions in dict, value is a Ranger command
        """

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

    def hide_git_files(self, hide_gitignore):
        """
        Hide the files included in gitignore.

        :param hide_gitignore bool: hide git ignore if True
        """

        if not hide_gitignore:
            return

        directory.wrap_dir_for_git()

    def load_user_settings(self, vanilla, urc_path):
        """
        Load user settings.


        :param vanilla bool: use default settings if True
        :param urc_path str: user rc path for settings
        """

        if vanilla:
            return

    def draw_border(self, draw_border, border_attr):
        """
        Using curses draw a border of floating window.

        :param draw_border bool: draw border if True
        :param border_attr dict: key contain 'fg' and 'bg', value's range is [-1-255]
        """
        if not draw_border:
            return

        from ranger.gui import color  # pylint: disable=import-outside-toplevel

        try:
            attr_fg, attr_bg = border_attr.get('fg', -1), border_attr.get('bg', -1)
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

        ui.enhance_draw_border(attr, self.fm.client)
        viewmiller.enhance_draw_border(attr)

    def change_view_adapt_size(self, views):
        """
        Ranger change view to adapt size of the floating window.

        :param views list: type of elements are dict
        """
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

    def kill_redundant_redraw(self):
        """
        I hate redundant redraw, eyes killer.

        """
        ui.skip_redraw()


OLD_HOOK_INIT = ranger.api.hook_init
ranger.fm.urc = Urc(ranger.fm, None)
ranger.api.hook_init = lambda fm: Hacks(fm, OLD_HOOK_INIT).hook_init()
