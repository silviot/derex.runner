from pathlib import Path
from typing import List
from typing import Optional
from typing import Union

import hashlib
import importlib_metadata
import os
import re


CONF_FILENAME = "derex.config.yaml"


def get_dir_hash(
    dirname: Union[Path, str],
    excluded_files: List = [],
    ignore_hidden: bool = False,
    followlinks: bool = False,
    excluded_extensions: List = [],
):
    """Given a directory return an hash based on its contents
    """
    if not os.path.isdir(dirname):
        raise TypeError(f"{dirname} is not a directory.")

    hashvalues = []
    for root, dirs, files in os.walk(dirname, topdown=True, followlinks=followlinks):
        if ignore_hidden and re.search(r"/\.", root):
            continue

        dirs.sort()
        files.sort()

        for filename in files:
            if ignore_hidden and filename.startswith("."):
                continue

            if filename.split(".")[-1:][0] in excluded_extensions:
                continue

            if filename in excluded_files:
                continue

            hasher = hashlib.sha256()
            filepath = os.path.join(root, filename)
            if not os.path.exists(filepath):
                hashvalues.append(hasher.hexdigest())
            else:
                with open(filepath, "rb") as fileobj:
                    while True:
                        data = fileobj.read(64 * 1024)
                        if not data:
                            break
                        hasher.update(data)
                hashvalues.append(hasher.hexdigest())

    hasher = hashlib.sha256()
    for hashvalue in sorted(hashvalues):
        hasher.update(hashvalue.encode("utf-8"))
    return hasher.hexdigest()


truthy = frozenset(("t", "true", "y", "yes", "on", "1"))


def asbool(s):
    """ Return the boolean value ``True`` if the case-lowered value of string
    input ``s`` is a `truthy string`. If ``s`` is already one of the
    boolean values ``True`` or ``False``, return it.
    Lifted from pyramid.settings.
    """
    if s is None:
        return False
    if isinstance(s, bool):
        return s
    s = str(s).strip()
    return s.lower() in truthy


def abspath_from_egg(egg: str, path: str) -> Optional[Path]:
    """Given a path relative to the egg root, find the absolute
    filesystem path for that resource.
    For instance this file's absolute path can be found passing
    derex/runner/utils.py
    to this function.
    """
    for file in importlib_metadata.files(egg):
        if str(file) == path:
            return file.locate()
    return None
