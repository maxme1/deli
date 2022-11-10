from os import PathLike
from typing import Any, BinaryIO, Union

from . import ExtensionMatch
from .helpers import SourceAgnostic
from ..serializer import MaybeHint, REGISTRY, Hint
from .packaged import Gzip


class Numpy(SourceAgnostic, ExtensionMatch):
    extensions = '.npy',

    def _match_value(self, value):
        return isinstance(value, (np.ndarray, np.generic))

    def load(self, source: Union[PathLike, BinaryIO], hint: MaybeHint, params) -> Any:
        return np.load(source, allow_pickle=False)

    def save(self, value: Any, destination: Union[PathLike, BinaryIO], hint: MaybeHint, params) -> Hint:
        np.save(destination, value, allow_pickle=False)
        return '.npy'


try:
    import numpy as np

    REGISTRY.append(Numpy())
    REGISTRY.append(Gzip(Numpy()))

except ImportError:
    pass
