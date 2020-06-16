"""
Patch ranger.gui.ui.UI

"""

import curses
from ranger.gui.ui import UI

def adapt_draw_border(attr, client):
    """
    Call by draw_border, fix UI to draw a border.

    :param attr int: attribute of curses
    :param client object: Object of attached neovim session
    """

    UI.update_size = _update_size

    _wrap_draw(attr)
    _wrap_initialize(client)
    _wrap_suspend(client)

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
