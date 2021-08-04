"""
Patch ranger.core.loader.Loadable

"""
import os
import subprocess
from ranger.core.shared import FileManagerAware
from ranger.core.loader import Loadable
from .. import rutil


class GitignoreLoader(Loadable, FileManagerAware):
    """
    Asynchronous callback from gitignore process.

    """

    def __init__(self, proc, path):
        self.proc = proc
        self.path = path
        Loadable.__init__(self, self.generate(), 'Asynchronous callback from gitignore process.')

    def generate(self):
        """
        Poll gitignore process until it have finished.

        """
        while True:
            try:
                out, err = self.proc.communicate(timeout=0.01)
                break
            except subprocess.TimeoutExpired:
                yield

        if err:
            self.fm.notify('GitignoreLoader callback error: {}'
                           .format(err.decode('utf-8')), bad=True)
            return

        fobj = self.fm.get_directory(self.path)
        fobj.ignored = [os.path.normpath(os.path.join(rutil.find_git_root(self.path), line[3:]))
                        for line in out.decode('utf-8').split('\0')[:-1]
                        if line.startswith('!! ')]
        fobj.ignore_proc = None

        if not fobj.settings.show_hidden:
            yield

            def gitignore_filter(f): return all([not rutil.is_subpath(ipath, f.path)
                                                 for ipath in fobj.ignored])
            fobj.files = [f for f in fobj.files if gitignore_filter(f) or
                          f.path == self.fm.attached_file]
            if fobj.files and not fobj.pointed_obj:
                fobj.pointed_obj = fobj.files[0]
            elif not fobj.files:
                fobj.pointed_obj = None
                fobj.correct_pointer()

            fobj.move_to_obj(fobj.pointed_obj)
            self.fm.ui.browser.request_clear()
            self.fm.ui.status.request_redraw()
