"""
Patch ranger.core.loader.Loadable

"""
import os
from ranger.core.shared import FileManagerAware
from ranger.core.loader import Loadable
from . import rutil

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
        while self.proc.poll() is None:
            yield
        out, err = self.proc.communicate()

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
            gitignore_filter = lambda f: all([not rutil.is_path_subset(ipath, f.path)
                                              for ipath in fobj.ignored])
            fobj.files = [f for f in fobj.files if gitignore_filter(f)]
            if fobj.files and not fobj.pointed_obj:
                fobj.pointed_obj = fobj.files[0]
            elif not fobj.files:
                fobj.pointed_obj = None
                fobj.correct_pointer()

            fobj.move_to_obj(fobj.pointed_obj)
            self.fm.ui.browser.request_clear()
            self.fm.ui.status.request_redraw()
