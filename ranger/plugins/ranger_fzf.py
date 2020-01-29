import subprocess
import os.path
from ranger.api.commands import Command


class FzfSelect(Command):
    """
    :fzf_select

    Find a file using fzf.

    With a prefix argument select only directories.

    See: https://github.com/junegunn/fzf
    """

    def execute(self):
        if self.quantifier:
            # match only directories
            command = r"find -L . -mindepth 1 \( -path '*/\.*' \
            -o -fstype 'dev' -o -fstype 'proc' \) -prune \
            -o -type d -print 2> /dev/null | cut -b3- | fzf +m"
        else:
            # match files and directories
            command = r"find -L . -mindepth 1 \( -path '*/\.*' \
            -o -fstype 'dev' -o -fstype 'proc' \) -prune \
            -o -print 2> /dev/null | cut -b3- | fzf +m"
        fzf = self.fm.execute_command(
            command, universal_newlines=True, stdout=subprocess.PIPE)
        stdout = fzf.communicate()[0]
        if fzf.returncode == 0:
            fzf_file = os.path.abspath(stdout.rstrip('\n'))
            print(fzf_file)
            if os.path.isdir(fzf_file):
                self.fm.cd(fzf_file)
            else:
                self.fm.select_file(fzf_file)
