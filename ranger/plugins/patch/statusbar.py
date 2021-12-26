"""
Patch ranger.gui.widgets.statusbar.StatusBar

"""

from ranger.gui.widgets.statusbar import StatusBar


def __init__(self, win, column=None):
    """
    https://github.com/ranger/ranger/pull/2005
    hijack the StatusBar's __init__

    """
    raw_init(self, win, column)
    for opt in ('hidden_filter', 'show_hidden'):
        self.settings.signal_bind('setopt.' + opt, self.request_redraw, weak=True)


raw_init = StatusBar.__init__
StatusBar.__init__ = __init__
