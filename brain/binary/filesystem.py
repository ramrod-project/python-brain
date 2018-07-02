"""
requires fuse

this file is covered by test_binary_filesystem.py
but
it is spawned as a background thread,
so codeclimate doens't see the coverage

set it to nocover
"""

from sys import stderr
import stat
from multiprocessing import Lock
from time import time
from collections import defaultdict
from io import BytesIO

noop = lambda *args, **kwargs: None  # :pragma-nocover #PEP-559


try:  # :pragma-nocover
    from fuse import FUSE, FuseOSError, Operations, c_stat, ENOENT, LoggingMixIn  # :pragma-nocover
    has_fuse = True  # :pragma-nocover
except ImportError as import_error:  # :pragma-nocover
    err_str = str(import_error)  # :pragma-nocover
    stderr.write("{1} - {0} requires fusepy\n".format(__name__, err_str))  # :pragma-nocover
    has_fuse = False  # :pragma-nocover
    FUSE = noop  # :pragma-nocover
    FuseOSError = None  # :pragma-nocover
    Operations = object  # :pragma-nocover
    c_stat = object  # :pragma-nocover

from .data import get, put, list_dir, delete
from .decorators import CONTENT_FIELD

VERBOSE = False
GET_DIR = [".", ".."]
ALLOW_LIST_DIR = True
ALLOW_REMOVE = False
READ_ONLY = False
MAX_CACHE_TIME = 600
OBJ_PERMISSION = 0o755


class NoStat(c_stat):  # pragma: no cover
    def __init__(self):  # pragma: no cover
        self.staged = False
        self.st_mode = 0
        self.st_ino = 0
        self.st_dev = 0
        self.st_nlink = 2
        self.st_uid = 0
        self.st_gid = 0
        self.st_size = 0
        self.st_atime = 0
        self.st_mtime = 0
        self.st_ctime = 0

    def as_dict(self):  # pragma: no cover
        return dict((key, getattr(self, key)) for key in ('st_atime',
                                                          'st_ctime',
                                                          'st_mtime',
                                                          'st_gid',
                                                          'st_mode',
                                                          'st_nlink',
                                                          'st_size',
                                                          'st_uid',
                                                          'st_ino'))


class BrainStore(LoggingMixIn, Operations):
    """
    read only filesystem
    getattr should raise FuseOSError(ENOENT) when brain file doesn't exist
       and
    implement the create/write functions to be r/w
    """
    def __init__(self):
        self.cache = dict()
        self.attr = defaultdict(dict)
        self.attr_lock = Lock()

    def read(self, path, size, offset, fh):  # pragma: no cover
        # print("read {}".format(path))
        return self.cache[path][offset:offset+size]

    def readdir(self, path, fh):  # pragma: no cover
        # print("readdir {}".format(path))
        return GET_DIR + list_dir() if ALLOW_LIST_DIR else []

    def _getattr_root(self, base):  # pragma: no cover
        base.st_mode = int(stat.S_IFDIR | OBJ_PERMISSION)
        base.st_nlink = 2
        return base

    def _getattr_pull_file_to_cache(self, base, path):  # pragma: no cover
        filename = path.strip("/")
        brain_data = get(filename) or {}
        if not brain_data and not READ_ONLY:
            raise FuseOSError(ENOENT)
        buf = brain_data.get(CONTENT_FIELD, b"")
        base.st_mode = stat.S_IFREG | OBJ_PERMISSION
        base.st_nlink = 1
        base.st_size = len(buf)
        self.cache[path] = buf
        self.attr[path] = {"ts": time(), "base": base, "staged": None}
        return base

    def _getattr_file(self, base, path):  # pragma: no cover
        now_time = time()
        if now_time - self.attr[path].get("ts", 0) > MAX_CACHE_TIME:
            base = self._getattr_pull_file_to_cache(base, path)
        else:
            base = self.attr[path]['base']
        return base

    def getattr(self, path, fh=None):  # pragma: no cover
        # print("attr {}".format(path))
        base = NoStat()
        if path == "/":
            base = self._getattr_root(base)
        else:
            with self.attr_lock:
                base = self._getattr_file(base, path)
        return base.as_dict()

    def create(self, path, mode):  # pragma: no cover
        """
        This is currently a read-only filessytem.
        GetAttr will return a stat for everything
        if getattr raises FuseOSError(ENOENT)
        OS may call this function and the write function
        """
        # print("create {}".format(path))
        now_time = time()
        with self.attr_lock:
            base = NoStat()
            base.staged = True
            base.st_mode = stat.S_IFREG | OBJ_PERMISSION
            base.st_nlink = 1
            base.st_size = -1
            self.attr[path] = {"ts": now_time, "base": base, "staged": BytesIO()}
        return mode

    def write(self, path, data, offset, fh):  # pragma: no cover
        """
        This is a readonly filesystem right now
        """
        # print("write {}".format(path))
        with self.attr_lock:
            base = self.attr[path]['base']
            staged = self.attr[path]['staged']
            if not staged.closed:
                base.st_size += len(data)
                staged.write(data)
        return len(data)

    def unlink(self, path):  # pragma: no cover
        # print("unlink {}".format(path))
        with self.attr_lock:
            if path in self.attr:
                del self.cache[path]
                del self.attr[path]
                if ALLOW_REMOVE:
                    delete(path.strip("/"))

    def _release_upload_to_brain(self, path):  # pragma: no cover
        base = self.attr[path]['base']
        filename = path.strip("/")
        staged = self.attr[path]["staged"]
        if base.staged and base.st_size > 0 and not staged.closed:
            io_val = staged.getvalue()
            staged.close()
            try:
                put({"id": filename, "Name": filename, "Content": io_val})
            except ValueError as ValErr:
                stderr.write("{}\n".format(ValErr))
            del self.attr[path]

    def release(self, path, fh):  # pragma: no cover
        # print("release {}".format(path))
        with self.attr_lock:
            self._release_upload_to_brain(path)
        self._cleanup()
        return 0

    def _cleanup(self):  # pragma: no cover
        """
        cleans up data that's been in the cache for a while

        should be called from an async OS call like release? to not impact user
        :return:
        """
        need_to_delete = []  # can't delete from a dict while iterating
        with self.attr_lock:
            now_time = time()
            for path in self.cache:
                if now_time - self.attr[path]['ts'] >= MAX_CACHE_TIME:
                    need_to_delete.append(path)
            for path in need_to_delete:
                del self.attr[path]
                del self.cache[path]


def start_filesystem(mountpoint):  # pragma: no cover
    """
    prgramatically mount this filesystem to some mount point
    :param mountpoint:
    :return:
    """
    if has_fuse:
        FUSE(BrainStore(), mountpoint, foreground=True)
    else:
        raise ImportError(err_str)
