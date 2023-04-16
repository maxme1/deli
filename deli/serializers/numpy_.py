from os import PathLike
from typing import Any, BinaryIO

from . import ExtensionMatch
from .packaged import Gzip
from ..serializer import MaybeHint, REGISTRY, Hint, WrongSerializer


class Numpy(ExtensionMatch):
    extensions = '.npy',

    def _match_value(self, value):
        return isinstance(value, (np.ndarray, np.generic))

    def save_buffer(self, value: Any, destination: BinaryIO, hint: MaybeHint, params: dict) -> Hint:
        np.save(destination, value, allow_pickle=False)
        return '.npy'

    def save_path(self, value: Any, destination: PathLike, hint: Hint, params: dict) -> Hint:
        np.save(destination, value, allow_pickle=False)
        return '.npy'

    def load_buffer(self, source: BinaryIO, hint: MaybeHint, allow_lazy: bool, params: dict) -> Any:
        # we'll try to read the numpy's magic constant if possible
        if hint is None and source.seekable():
            position = source.tell()
            if source.read(6) != b'\x93NUMPY':
                raise WrongSerializer
            source.seek(position)

        return np.load(source, allow_pickle=False)

    def load_path(self, source: PathLike, hint: Hint, params: dict) -> Any:
        if hint is None:
            with open(source, 'rb') as file:
                if file.read(6) != b'\x93NUMPY':
                    raise WrongSerializer

        return np.load(source, allow_pickle=False)


try:
    import numpy as np

    REGISTRY.append(Numpy())
    REGISTRY.append(Gzip(Numpy()))

except ImportError:
    pass
