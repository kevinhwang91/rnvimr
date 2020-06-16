"""
Patch ranger.gui.widgets.view_miller.ViewMiller

"""

import inspect
import textwrap
import curses
from ranger.gui.widgets.view_miller import ViewMiller


def adapt_draw_border(attr):
    """
    Call by draw_border, fix ViewMiller can't draw border properly.

    :param attr int: attribute of curses
    """

    _wrap_resize()
    _wrap_draw_border(attr)


def _wrap_resize():
    code = textwrap.dedent(inspect.getsource(ViewMiller.resize))
    code = code.replace('def resize', 'def view_miller_resize')
    code = code.replace('left = pad', 'left = 0')
    code = code.replace('wid = int(self.wid - left + 1 - pad)',
                        'wid = int(self.wid - left + 1)')

    wrapped_module = inspect.getmodule(ViewMiller)
    exec(code, wrapped_module.__dict__)  # pylint: disable=exec-used

    ViewMiller.resize = wrapped_module.view_miller_resize


def _wrap_draw_border(attr):
    def draw_border(self, border_types):
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

    ViewMiller._draw_borders = draw_border  # pylint: disable=protected-access
