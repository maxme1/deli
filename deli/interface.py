import json
import os
import pickle
from gzip import GzipFile
from os import PathLike
from typing import Any, Union, BinaryIO

from .serializer import MaybeHint, WrongSerializer, REGISTRY
from .serializers.choice import Choice

__all__ = [
    'load', 'save',
    'load_json', 'save_json',
    'load_pickle', 'save_pickle',
    'load_numpy', 'save_numpy',
    'load_csv', 'save_csv',
    'load_text', 'save_text',
]


def load(source: Union[str, PathLike, BinaryIO], hint: MaybeHint = None, **kwargs):
    """
    Load a value from a file-like or buffer `source`.
    `hint` is used to override the format detection.
    `kwargs` are format-specific keyword arguments.
    """
    choice = Choice(*REGISTRY)

    if isinstance(source, (str, PathLike)):
        if hint is None:
            hint = os.path.basename(os.fspath(source))

        try:
            return choice.load_path(source, hint, kwargs)
        except WrongSerializer:
            pass

        with open(source, 'rb') as buffer:
            return choice.load_buffer(buffer, hint, False, kwargs)

    if not isinstance(source, BinaryIO):
        raise TypeError('Need a binary buffer')

    return choice.load_buffer(source, hint, True, kwargs)


def save(value: Any, destination: Union[str, PathLike, BinaryIO], hint: MaybeHint = None, **kwargs) -> str:
    """
    Save `value` to a file-like or buffer `destination`.
    `hint` is used to override the format detection.
    `kwargs` are format-specific keyword arguments.
    """
    choice = Choice(*REGISTRY)

    if isinstance(destination, (str, PathLike)):
        if hint is None:
            hint = os.path.basename(os.fspath(destination))

        try:
            return choice.save_path(value, destination, hint, kwargs)
        except WrongSerializer:
            pass

        with open(destination, 'wb') as buffer:
            return choice.save_buffer(value, buffer, hint, kwargs)

    if not isinstance(destination, BinaryIO):
        raise TypeError('Need a binary buffer')

    return choice.save_buffer(value, destination, hint, kwargs)


def load_json(path: PathLike):
    """Load the contents of a json file."""
    with open(path, 'r') as f:
        return json.load(f)


def save_json(value, path: PathLike, *, indent: int = None):
    """Dump a json-serializable object to a json file."""
    with open(path, 'w') as f:
        json.dump(value, f, indent=indent)


def save_numpy(value, path: PathLike, *, allow_pickle: bool = True, fix_imports: bool = True, compression: int = None,
               timestamp: int = None):
    """A wrapper around ``np.save`` that matches the interface ``save(what, where)``."""
    import numpy as np

    if compression is not None:
        with GzipFile(path, 'wb', compresslevel=compression, mtime=timestamp) as file:
            return save_numpy(value, file, allow_pickle=allow_pickle, fix_imports=fix_imports)

    np.save(path, value, allow_pickle=allow_pickle, fix_imports=fix_imports)


def load_numpy(path: PathLike, *, allow_pickle: bool = False, fix_imports: bool = True, decompress: bool = False):
    """A wrapper around ``np.load``"""
    import numpy as np

    if decompress:
        with GzipFile(path, 'rb') as file:
            return load_numpy(file, allow_pickle=allow_pickle, fix_imports=fix_imports)

    return np.load(path, allow_pickle=allow_pickle, fix_imports=fix_imports)


def save_pickle(value, path: PathLike):
    """Pickle a ``value`` to ``path``."""
    with open(path, 'wb') as file:
        pickle.dump(value, file)


def load_pickle(path: PathLike):
    """Load a pickled value from ``path``."""
    with open(path, 'rb') as file:
        return pickle.load(file)


def save_text(value: str, path: PathLike):
    with open(path, mode='w') as file:
        file.write(value)


def load_text(path: PathLike):
    with open(path, mode='r') as file:
        return file.read()


def save_csv(value, path: PathLike, *, compression: int = None, **kwargs):
    if compression is not None:
        kwargs['compression'] = {
            'method': 'gzip',
            'compresslevel': compression,
        }

    value.to_csv(path, **kwargs)


def load_csv(path: PathLike, **kwargs):
    import pandas as pd
    return pd.read_csv(path, **kwargs)
