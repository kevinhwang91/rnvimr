"""
Patch ranger.container.directory.Directory

"""

import os.path
import re
import subprocess
from os import lstat as os_lstat
from os import stat as os_stat
from time import time

import ranger.container.directory
from ranger.container.directory import Directory, InodeFilterConstants
from ranger.container.file import File
from ranger.ext.human_readable import human_readable
from ranger.ext.mount_path import mount_path

from .loader import GitignoreLoader
from .. import rutil


def wrap_dir_for_git():
    """
    Wrap directory for hidden git ignored files.

    """
    Directory.load_bit_by_bit = load_bit_by_bit
    Directory.refilter = refilter
    Directory.load_content_if_outdated = load_content_if_outdated


def _walklevel(some_dir, level):
    some_dir = some_dir.rstrip(os.path.sep)
    followlinks = level > 0
    assert os.path.isdir(some_dir)
    num_sep = some_dir.count(os.path.sep)
    for root, dirs, files in os.walk(some_dir, followlinks=followlinks):
        if '.git' in dirs:
            dirs.remove('.git')
        yield root, dirs, files
        num_sep_this = root.count(os.path.sep)
        if level != -1 and num_sep + level <= num_sep_this:
            del dirs[:]


def _mtimelevel(path, level):
    mtime = os.stat(path).st_mtime
    for dirpath, dirnames, _ in _walklevel(path, level):
        dirlist = [os.path.join("/", dirpath, d) for d in dirnames
                   if level == -1 or dirpath.count(os.path.sep) - path.count(os.path.sep) <= level]
        mtime = max(mtime, max([-1] + [os.stat(d).st_mtime for d in dirlist]))
    return mtime


def _build_git_ignore_process(fobj):
    git_root = rutil.find_git_root(fobj.path)
    if git_root:
        grfobj = fobj.fm.get_directory(git_root)
        if grfobj.load_content_mtime > fobj.load_content_mtime and hasattr(grfobj, 'ignored'):
            fobj.ignored = [ignored for ignored in grfobj.ignored
                            if rutil.is_subpath(ignored, fobj.path) or
                            os.path.dirname(ignored) == fobj.path]
        else:
            git_ignore_cmd = ['git', 'status', '--ignored', '-z', '--porcelain', '.']
            fobj.ignore_proc = subprocess.Popen(git_ignore_cmd, cwd=fobj.path,
                                                stdout=subprocess.PIPE,
                                                stderr=subprocess.PIPE)
            fobj.fm.loader.add(GitignoreLoader(fobj.ignore_proc, fobj.path), append=True)


def load_bit_by_bit(self):
    """
    Almost code is copied from ranger.
    An iterator that loads a part on every next() call

    Returns a generator which load a part of the directory
    in each iteration.
    """

    self.ignore_proc = None
    self.loading = True
    self.percent = 0
    self.load_if_outdated()

    basename_is_rel_to = self.path if self.flat else None

    try:  # pylint: disable=too-many-nested-blocks
        if self.runnable:
            yield
            mypath = self.path

            self.mount_path = mount_path(mypath)

            if self.flat:
                filelist = []
                for dirpath, dirnames, filenames in _walklevel(mypath, self.flat):
                    dirlist = [
                        os.path.join("/", dirpath, d)
                        for d in dirnames
                        if self.flat == -1
                        or (dirpath.count(os.path.sep)
                            - mypath.count(os.path.sep)) <= self.flat
                    ]
                    filelist += dirlist
                    filelist += [os.path.join("/", dirpath, f) for f in filenames]
                filenames = filelist
                self.load_content_mtime = _mtimelevel(mypath, self.flat)
            else:
                filelist = os.listdir(mypath)
                filenames = [mypath + (mypath == '/' and fname or '/' + fname)
                             for fname in filelist]
                self.load_content_mtime = os.stat(mypath).st_mtime

            _build_git_ignore_process(self)

            if self.cumulative_size_calculated:
                # If self.content_loaded is true, this is not the first
                # time loading.  So I can't really be sure if the
                # size has changed and I'll add a "?".
                if self.content_loaded:
                    if self.fm.settings.autoupdate_cumulative_size:
                        self.look_up_cumulative_size()
                    else:
                        self.infostring = ' %s' % human_readable(
                            self.size, separator='? ')
                else:
                    self.infostring = ' %s' % human_readable(self.size)
            else:
                self.size = len(filelist)
                self.infostring = ' %d' % self.size
            if self.is_link:
                self.infostring = '->' + self.infostring

            yield

            marked_paths = [obj.path for obj in self.marked_items]

            files = []
            disk_usage = 0

            has_vcschild = False
            for name in filenames:
                try:
                    file_lstat = os_lstat(name)
                    if file_lstat.st_mode & 0o170000 == 0o120000:
                        file_stat = os_stat(name)
                    else:
                        file_stat = file_lstat
                except OSError:
                    file_lstat = None
                    file_stat = None
                if file_lstat and file_stat:
                    stats = (file_stat, file_lstat)
                    is_a_dir = file_stat.st_mode & 0o170000 == 0o040000
                else:
                    stats = None
                    is_a_dir = False

                if is_a_dir:
                    item = self.fm.get_directory(name, preload=stats, path_is_abs=True,
                                                 basename_is_rel_to=basename_is_rel_to)
                    item.load_if_outdated()
                    if self.flat:
                        item.relative_path = os.path.relpath(item.path, self.path)
                    else:
                        item.relative_path = item.basename
                    item.relative_path_lower = item.relative_path.lower()
                    if item.vcs and item.vcs.track:
                        if item.vcs.is_root_pointer:
                            has_vcschild = True
                        else:
                            item.vcsstatus = \
                                item.vcs.rootvcs.status_subpath(  # pylint: disable=no-member
                                    os.path.join(self.realpath, item.basename),
                                    is_directory=True,
                                )
                else:
                    item = File(name, preload=stats, path_is_abs=True,
                                basename_is_rel_to=basename_is_rel_to)
                    item.load()
                    disk_usage += item.size
                    if self.vcs and self.vcs.track:
                        item.vcsstatus = \
                            self.vcs.rootvcs.status_subpath(  # pylint: disable=no-member
                                os.path.join(self.realpath, item.basename))

                files.append(item)
                self.percent = 100 * len(files) // len(filenames)
                yield
            self.has_vcschild = has_vcschild
            self.disk_usage = disk_usage

            self.filenames = filenames
            self.files_all = files

            self._clear_marked_items()  # pylint: disable=protected-access
            for item in self.files_all:
                if item.path in marked_paths:
                    item.mark_set(True)
                    self.marked_items.append(item)
                else:
                    item.mark_set(False)

            self.sort()

            if files:
                if self.pointed_obj is not None:
                    self.sync_index()
                else:
                    self.move(to=0)
        else:
            self.filenames = None
            self.files_all = None
            self.files = None

        self.cycle_list = None
        self.content_loaded = True
        self.last_update_time = time()
        self.correct_pointer()

    finally:
        self.loading = False
        self.fm.signal_emit("finished_loading_dir", directory=self)
        if self.vcs:
            self.fm.ui.vcsthread.process(self)


def refilter(self):
    """
    Almost code is copied from ranger.

    """
    if self.files_all is None:
        return  # propably not loaded yet

    self.last_update_time = time()

    filters = []

    if not self.settings.show_hidden and self.settings.hidden_filter:
        hidden_filter = re.compile(self.settings.hidden_filter)
        hidden_filter_search = hidden_filter.search

        def hidden_filter_func(fobj):
            # always show attached file.
            if fobj.path != self.fm.attached_file:
                for comp in fobj.relative_path.split(os.path.sep):
                    if hidden_filter_search(comp):
                        return False
            return True
        filters.append(hidden_filter_func)

    if self.narrow_filter:
        # pylint: disable=unsupported-membership-test

        # Pylint complains that self.narrow_filter is by default
        # None but the execution won't reach this line if it is
        # still None.
        filters.append(lambda fobj: fobj.basename in self.narrow_filter)
    if self.settings.global_inode_type_filter or self.inode_type_filter:
        def inode_filter_func(obj):
            # Use local inode_type_filter if present, global otherwise
            inode_filter = self.inode_type_filter or self.settings.global_inode_type_filter
            # Apply filter
            if InodeFilterConstants.DIRS in inode_filter and obj.is_directory:
                return True
            if InodeFilterConstants.FILES in inode_filter and obj.is_file and not obj.is_link:
                return True
            if InodeFilterConstants.LINKS in inode_filter and obj.is_link:
                return True
            return False
        filters.append(inode_filter_func)
    if self.filter:
        filter_search = self.filter.search
        filters.append(lambda fobj: filter_search(fobj.basename))
    if self.temporary_filter:
        temporary_filter_search = self.temporary_filter.search
        filters.append(lambda fobj: temporary_filter_search(fobj.basename))
    filters.extend(self.filter_stack)

    if not self.settings.show_hidden:
        if hasattr(self, 'ignored'):
            filters.append(
                lambda fobj: all([not rutil.is_subpath(ipath, fobj.path)
                                  for ipath in self.ignored]) or fobj.path == self.fm.attached_file)

    self.files = [f for f in self.files_all if ranger.container.directory.accept_file(f, filters)]

    # A fix for corner cases when the user invokes show_hidden on a
    # directory that contains only hidden directories and hidden files.
    if self.files and not self.pointed_obj:
        self.pointed_obj = self.files[0]
    elif not self.files:
        self.pointed_obj = None
        self.correct_pointer()

    self.move_to_obj(self.pointed_obj)


def load_content_if_outdated(self, *a, **k):
    """Load the contents of the directory if outdated"""

    if self.load_content_once(*a, **k):
        return True

    if self.files_all is None or self.content_outdated:
        self.load_content(*a, **k)
        return True

    try:
        if self.flat:
            real_mtime = _mtimelevel(self.path, self.flat)
        else:
            real_mtime = os.stat(self.path).st_mtime
    except OSError:
        real_mtime = None
        return False
    if self.stat:
        cached_mtime = self.load_content_mtime
    else:
        cached_mtime = 0

    if real_mtime != cached_mtime:
        self.load_content(*a, **k)
        return True
    return False
