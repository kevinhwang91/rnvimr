"""
Patch ranger.ext.img_display.UeberzugImageDisplayer

"""

from ranger.ext.img_display import UeberzugImageDisplayer


def wrap_draw(client):
    """
    Wrap Ueberzug draw method.

    :param client object: Object of attached neovim session
    """

    # pylint: disable=too-many-arguments
    def draw(self, path, start_x, start_y, width, height):
        win_info = client.get_window_info()
        if not win_info.get('relative', None):
            return
        start_x += win_info['col']
        start_y += win_info['row']

        raw_draw(self, path, start_x, start_y, width, height)

    raw_draw = UeberzugImageDisplayer.draw
    UeberzugImageDisplayer.draw = draw
