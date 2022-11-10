from os import PathLike
from typing import Any, BinaryIO, Union

from ..serializer import MaybeHint, REGISTRY, Hint, WrongSerializer
from .helpers import ExtensionMatch, SourceAgnostic


class ImageIO(ExtensionMatch, SourceAgnostic):
    extensions = '.png', '.jpg', '.tif', '.bmp',

    def _match_value(self, value):
        return isinstance(value, np.ndarray)

    def load(self, source: Union[PathLike, BinaryIO], hint: MaybeHint, params) -> Any:
        if hint is not None:
            hint = '.' + hint.split('.')[-1]
        return imread(source, extension=hint)

    def save(self, value: Any, destination: Union[PathLike, BinaryIO], hint: MaybeHint, params) -> Hint:
        if hint is None:
            raise WrongSerializer

        hint = '.' + hint.split('.')[-1]
        imwrite(destination, value, extension=hint)
        return hint


try:
    try:
        from imageio.v3 import imread, imwrite
    except ImportError:
        # py3.6
        from imageio import imread as _imread, imwrite as _imwrite


        def imread(x, extension):
            return _imread(x, format=extension)


        def imwrite(x, y, extension):
            return _imwrite(x, y, format=extension)

    import numpy as np

    REGISTRY.append(ImageIO())

except ImportError:
    pass
