"""
Patch ranger.config.commands

"""

import os
import tempfile
import shlex


def enhance_quit(commands, client):
    """
    Make ranger pretend to quit.

    :param commands dict: command name as key, command class as val
    :param client object: Object of attached neovim session
    """

    quit_cls = commands.get_command('quit')
    if not quit_cls:
        return

    def execute(self):

        if len(self.fm.tabs) >= 2:
            self.fm.tab_close()
        else:
            client.hide_window()
            self.fm.execute_console('ClearImage')

    quit_cls.execute = execute


def enhance_bulkrename(commands, client):
    """
    Bulkrename need a block workflow, so restore the raw editor to edit file name.
    Enhance bulkrename to save information in loaded buffers.

    :param commands dict: command name as key, command class as val
    :param client object: Object of attached neovim session
    """

    bulkrename_cls = commands.get_command('bulkrename')
    if not bulkrename_cls:
        return

    def _parse_cmd_and_move_buf(content):
        for line in content.decode('utf-8').splitlines():
            cmd = shlex.split(line, comments=True)
            if cmd:
                try:
                    src, dst = cmd[-2:]
                except ValueError:
                    pass
                else:
                    client.move_buf(os.path.abspath(src), os.path.abspath(dst))

    def execute(self):  # pylint: disable=too-many-locals
        from ranger.container.file import File  # pylint: disable=import-outside-toplevel
        # pylint: disable=import-outside-toplevel
        from ranger.ext.shell_escape import shell_escape as esc

        editor = os.getenv('EDITOR')
        if not editor:
            editor = 'nvim'

        # Create and edit the file list
        filenames = [f.relative_path for f in self.fm.thistab.get_selection()]
        with tempfile.NamedTemporaryFile(delete=False) as listfile:
            listpath = listfile.name
            listfile.write('\n'.join(filenames).encode(encoding='utf-8', errors='surrogateescape'))
        self.fm.execute_file([File(listpath)], app=editor)
        with open(listpath, 'r', encoding='utf-8', errors='surrogateescape') as listfile:
            new_filenames = listfile.read().split("\n")
        os.unlink(listpath)
        if all(a == b for a, b in zip(filenames, new_filenames)):
            self.fm.notify('No renaming to be done!')
            return

        # Generate script
        with tempfile.NamedTemporaryFile() as cmdfile:
            script_lines = []
            script_lines.append('# This file will be executed when you close the editor.')
            script_lines.append('# Please double-check everything, clear the file to abort.')
            new_dirs = []
            for old, new in zip(filenames, new_filenames):
                if old != new:
                    basepath, _ = os.path.split(new)
                    if (basepath and basepath not in new_dirs and not os.path.isdir(basepath)):
                        basepath = esc(basepath)
                        script_lines.append(f'mkdir -vp -- {basepath}')
                        new_dirs.append(basepath)
                        old, new = esc(old), esc(new)
                    script_lines.append(f'mv -vi -- {old} {new}')
            # Make sure not to forget the ending newline
            script_content = '\n'.join(script_lines) + '\n'
            cmdfile.write(script_content.encode(encoding='utf-8', errors='surrogateescape'))
            cmdfile.flush()

            # Open the script and let the user review it, then check if the
            # script was modified by the user
            self.fm.execute_file([File(cmdfile.name)], app=editor)
            cmdfile.seek(0)
            new_content = cmdfile.read()
            script_was_edited = (script_content != new_content)

            # Do the renaming
            self.fm.run(['/bin/sh', cmdfile.name], flags='w')

            _parse_cmd_and_move_buf(new_content)

        # Retag the files, but only if the script wasn't changed during review,
        # because only then we know which are the source and destination files.
        if not script_was_edited:
            tags_changed = False
            for old, new in zip(filenames, new_filenames):
                if old != new:
                    oldpath = self.fm.thisdir.path + '/' + old
                    newpath = self.fm.thisdir.path + '/' + new
                    if oldpath in self.fm.tags:
                        old_tag = self.fm.tags.tags[oldpath]
                        self.fm.tags.remove(oldpath)
                        self.fm.tags.tags[newpath] = old_tag
                        tags_changed = True
            if tags_changed:
                self.fm.tags.dump()
        else:
            self.fm.notify('files have not been retagged')

    bulkrename_cls.execute = execute
