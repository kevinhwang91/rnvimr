"""
Load user setting
"""

import os
import sys
from logging import getLogger
import ranger

LOG = getLogger(__name__)


def _load_commands(fm):  # pylint: disable=invalid-name
    commands_path = fm.confpath('commands.py')
    if os.path.exists(commands_path):
        from .rutil import dynamic_import  # pylint: disable=import-outside-toplevel
        try:
            module = dynamic_import('commands', commands_path)
        except ImportError as ex:
            LOG.debug("Failed to import custom commands from '%s'", commands_path)
            LOG.exception(ex)
        else:
            fm.commands.load_commands_from_module(module)
            LOG.debug("Loaded custom commands from '%s'", commands_path)


def _load_plugins(fm):  # pylint: disable=invalid-name
    plug_dir = fm.confpath('plugins')
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
                    ex_msg = "Error while loading plugin '{0}'".format(module_base)
                    LOG.error(ex_msg)
                    LOG.exception(ex)
                else:
                    fm.commands.load_commands_from_module(module)
                    LOG.debug("Loaded plugin '%s'", module_base)

    if sys.path[0] == plug_dir:
        del sys.path[0]


def _load_rc(fm):  # pylint: disable=invalid-name
    #  set use_preview_script may cause a bad notify when ui is on
    o_ui_status = fm.ui.is_on
    fm.ui.is_on = False
    custom_conf = fm.confpath('rc.conf')
    if os.access(custom_conf, os.R_OK):
        fm.source(custom_conf)
    fm.ui.is_on = o_ui_status


def _reload_rifle(fm):  # pylint: disable=invalid-name

    if os.access(fm.confpath('rifle.conf'), os.R_OK):
        fm.rifle.config_file = fm.confpath('rifle.conf')
        fm.rifle.reload_config()


def load_user_settings(fm, confdir=None):  # pylint: disable=invalid-name
    """
    Load user setting because rnvimr occupy confdir when ranger startup

    :param fm Object: ranger context
    :param confdir str: config directory
    """

    if not confdir:
        xdg_path = os.environ.get('XDG_CONFIG_HOME')
        if xdg_path and os.path.isabs(xdg_path):
            confdir = os.path.join(xdg_path, 'ranger')
        if not confdir:
            confdir = os.path.expanduser('~/.config/ranger')

    ranger.args.confdir = confdir

    _load_commands(fm)
    _load_plugins(fm)
    _load_rc(fm)
    _reload_rifle(fm)
