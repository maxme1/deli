from io import RawIOBase, BufferedIOBase
import os
from gzip import GzipFile
from os import PathLike
from typing import Any, Optional, Union, BinaryIO

from .serializer import MaybeHint, WrongSerializer, REGISTRY, Hint
from .serializers.choice import Choice

__all__ = [
    'load', 'save',
    'load_json', 'save_json',
    'load_pickle', 'save_pickle',
    'load_numpy', 'save_numpy',
    'load_csv', 'save_csv',
    'load_text', 'save_text',
]


def load(source: Union[str, PathLike, BinaryIO], hint: MaybeHint = None, **kwargs) -> Any:
    """
    Load a value from a file-like or buffer `source`.
    `hint` is used to override the format detection.
    `kwargs` are format-specific keyword arguments.
    """
    choice = Choice(*REGISTRY)

    hint = _resolve_hint(hint, source)
    strict = hint is not None
    # TODO: what is it's both BinaryIO and PathLike?
    if isinstance(source, (str, PathLike)):
        loader = choice
        if strict:
            loader = choice.match_load_path(source, hint, kwargs)
            if loader is None:
                raise WrongSerializer(f"Couldn't load from value using {hint!r} as hint")

        return loader.load_path(source, hint, kwargs)

    if not is_binary_io(source):
        raise TypeError(f'Need a binary buffer, not {type(source).__name__}')

    # TODO: reuse
    loader = choice
    if strict:
        loader = choice.match_load_buffer(hint, True, kwargs)
        if loader is None:
            raise WrongSerializer(f"Couldn't load from value using {hint!r} as hint")

    return loader.load_buffer(source, hint, True, kwargs)


def save(value: Any, destination: Union[str, PathLike, BinaryIO], hint: MaybeHint = None, **kwargs) -> Hint:
    """
    Save `value` to a file-like or buffer `destination`.
    `hint` is used to override the format detection.
    `kwargs` are format-specific keyword arguments.
    """
    choice = Choice(*REGISTRY)

    hint = _resolve_hint(hint, destination)
    strict = hint is not None
    # TODO: what if it's both BinaryIO and PathLike?
    if isinstance(destination, (str, PathLike)):
        loader = choice
        if strict:
            loader = choice.match_save_path(value, destination, hint, kwargs)
            if loader is None:
                raise WrongSerializer(f"Couldn't save value using {hint!r} as hint")

        return loader.save_path(value, destination, hint, kwargs)

    if not is_binary_io(destination):
        raise TypeError(f'Need a binary buffer, not {type(destination).__name__}')

    # TODO: reuse
    loader = choice
    if strict:
        loader = choice.match_save_buffer(value, hint, kwargs)
        if loader is None:
            raise WrongSerializer(f"Couldn't save value using {hint!r} as hint")

    return loader.save_buffer(value, destination, hint, kwargs)


def _resolve_hint(hint, path) -> MaybeHint:
    assert isinstance(hint, (str, bool)) or hint is None, hint
    if hint is None:
        hint = True
    if isinstance(hint, str):
        return hint
    if not hint:
        return None
    if isinstance(path, (str, PathLike)):
        return os.path.basename(os.fspath(path))
    return None


def load_json(path: PathLike):
    """Load the contents of a json file."""
    return load(path, hint='.json')


def save_json(value, path: PathLike, *, indent: Optional[int] = None):
    """Dump a json-serializable object to a json file."""
    save(value, path, hint='.json', indent=indent)


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
    save(value, path, hint='.pkl')


def load_pickle(path: PathLike):
    """Load a pickled value from ``path``."""
    return load(path, hint='.pkl')


def save_text(value: str, path: PathLike):
    save(value, path, hint='.txt')
    

def load_text(path: PathLike):
    return load(path, hint='.txt')


def save_csv(value, path: PathLike, *, compression: Optional[int] = None, **kwargs):
    if compression is not None:
        kwargs['compression'] = {
            'method': 'gzip',
            'compresslevel': compression,
        }

    value.to_csv(path, **kwargs)


def load_csv(path: PathLike, **kwargs):
    return load(path, hint='.csv', **kwargs)


def is_binary_io(x):
    return isinstance(x, (BinaryIO, RawIOBase, BufferedIOBase))
