"""
Patch ranger.gui.ui.UI

"""

import curses
from ranger.gui.ui import UI


def enhance_draw_border(attr, client):
    """
    Call by draw_border, fix UI to draw a border.

    :param attr int: Attribute of curses.
    :param client object: Object of attached neovim session.
    """

    UI.update_size = _update_size

    _wrap_draw(attr)
    _wrap_initialize(client)
    _wrap_suspend(client)


def wrap_update_size(views):
    """
    Wrap update_size method.

    :param views list: Views for ranger to change viewmode and column_ratios.
    """

    def update_size(self):

        raw_update_size(self)
        _change_view(views, self.fm)

    raw_update_size = UI.update_size
    UI.update_size = update_size


def _change_view(views, fm):  # pylint: disable=invalid-name
    win_info = fm.client.get_window_info()
    if win_info.get('relative', None):
        win_width = win_info['width']
        cur_col_ratio = fm.settings['column_ratios']
        cur_viewmode = fm.settings['viewmode']
        for view in views:
            if view['minwidth'] <= win_width <= view['maxwidth']:
                ratio = view['ratio']
                viewmode = view['viewmode']
                if viewmode != cur_viewmode:
                    fm.execute_console('set viewmode!')
                if viewmode == 'miller' and cur_col_ratio != ratio:
                    #  TODO displayable.resize will complain subwindow size out of bonds,
                    # it seems that this issue is caused by neovim terminal.
                    raw_notify = fm.notify
                    fm.notify = lambda obj, **kw: None
                    fm.execute_console('set column_ratios {}'.format(','.join(map(str, ratio))))
                    fm.notify = raw_notify
                break


def _update_size(self):
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


def _wrap_draw(attr):
    def draw(self):
        self.win.attrset(attr)
        self.win.border(curses.ACS_VLINE, curses.ACS_VLINE, curses.ACS_HLINE,
                        curses.ACS_HLINE, curses.ACS_ULCORNER, curses.ACS_URCORNER,
                        curses.ACS_LLCORNER, curses.ACS_LRCORNER)
        raw_draw(self)

    raw_draw = UI.draw
    UI.draw = draw


def _wrap_initialize(client):
    def initialize(self):
        client.set_winhl('curses_winhl')
        raw_initialize(self)

    raw_initialize = UI.initialize
    UI.initialize = initialize


def _wrap_suspend(client):
    def suspend(self):
        def check_destroy():
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
        #  destroy don't restore the NormalFloat highlight
        if not check_destroy():
            client.set_winhl('normal_winhl')

    raw_suspend = UI.suspend
    UI.suspend = suspend


def wrap_pager():
    """
    Wrap UI open_pager and close_pager method.

    """

    def open_pager(self):
        pager = raw_open_pager(self)
        pager.scroll_begin = self.browser.columns[-1].scroll_extra
        return pager

    def close_pager(self):
        self.browser.columns[-1].scroll_extra = self.pager.scroll_begin
        raw_close_pager(self)

    raw_open_pager = UI.open_pager
    raw_close_pager = UI.close_pager
    UI.open_pager = open_pager
    UI.close_pager = close_pager
