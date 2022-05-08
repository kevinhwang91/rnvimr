"""
Load user setting
"""

import os
import sys
from logging import getLogger
import ranger

LOG = getLogger(__name__)


class Urc():
    """
    User rc settings
    """

    def __init__(self, fm):  # pylint: disable=invalid-name
        self.fm = fm  # pylint: disable=invalid-name

    def load_commands(self):
        """
        load users' commands, like `load_settings(fm, clean)` in main.py
        """
        commands_path = self.fm.confpath('commands.py')
        if os.path.exists(commands_path):
            from .rutil import dynamic_import  # pylint: disable=import-outside-toplevel
            try:
                module = dynamic_import('commands', commands_path)
            except ImportError as ex:
                LOG.debug("Failed to import custom commands from '%s'", commands_path)
                LOG.exception(ex)
            else:
                self.fm.commands.load_commands_from_module(module)
                LOG.debug("Loaded custom commands from '%s'", commands_path)

    def load_plugins(self):  # pylint: disable=invalid-name
        """
        load users' plugins, like `load_settings(fm, clean)` in main.py
        """
        plug_dir = self.fm.confpath('plugins')
        if plug_dir not in sys.path:
            sys.path.insert(0, plug_dir)
        try:
            plugin_files = sorted(os.listdir(plug_dir))
        except OSError:
            LOG.debug('Unable to access plugin directory: %s', plug_dir)
        else:
            for plugin in plugin_files:
                if plugin.startswith('_'):
                    continue

                module_base = None
                module_path = os.path.join(plug_dir, plugin)
                if plugin.endswith('.py'):
                    module_base = plugin[:-3]
                elif os.path.isdir(module_path):
                    module_base = plugin

                if module_base:
                    from importlib import import_module  # pylint: disable=import-outside-toplevel
                    try:
                        module = import_module(module_base)
                    except Exception as ex:  # pylint: disable=broad-except
                        ex_msg = f"Error while loading plugin '{module_base}'"
                        LOG.error(ex_msg)
                        LOG.exception(ex)
                    else:
                        self.fm.commands.load_commands_from_module(module)
                        LOG.debug("Loaded plugin '%s'", module_base)

        if sys.path[0] == plug_dir:
            del sys.path[0]

    def redirect_and_load(self):
        """
        Load user setting because rnvimr occupy confdir when ranger startup

        """
        if os.getenv('RNVIMR_VANILLA'):
            if os.environ.get('RANGER_LOAD_DEFAULT_RC', 'TRUE').upper() == 'FALSE':
                default_conf = self.fm.relpath('config', 'rc.conf')
                self.fm.source(default_conf)
            return

        confdir = None
        urc_path = os.getenv('RNVIMR_URC_PATH')
        if urc_path:
            confdir = os.path.expanduser(urc_path)
        else:
            xdg_path = os.environ.get('XDG_CONFIG_HOME')
            if xdg_path and os.path.isabs(xdg_path):
                confdir = os.path.join(xdg_path, 'ranger')
            if not confdir:
                confdir = os.path.expanduser('~/.config/ranger')

        ranger.args.confdir = confdir
        custom_conf = self.fm.confpath('rc.conf')
        self.load_commands()
        self.load_plugins()
        self.fm.source(custom_conf)
