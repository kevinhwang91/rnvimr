"""
Patch ranger.ext.rifle.Rifle

"""

from ranger.ext.rifle import Rifle


def build_fake_editor(client, edit_cmd):
    """
    Build a fake editor.

    :param client object: Object of attached neovim session
    """

    def build_command(self, files, action, flags):
        if '$EDITOR' in action:
            client.rpc_edit(files, edit=edit_cmd)
            self._app_flags = 'f'  # pylint: disable=protected-access
            return 'true'
        return raw_build_command(self, files, action, flags)

    raw_build_command = Rifle._build_command  # pylint: disable=protected-access
    Rifle._build_command = build_command  # pylint: disable=protected-access
