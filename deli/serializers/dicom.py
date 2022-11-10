from os import PathLike
from typing import BinaryIO, Any, Union

from ..serializer import MaybeHint, REGISTRY, Hint
from .helpers import ExtensionMatch, SourceAgnostic
from .packaged import Gzip


class DICOM(ExtensionMatch, SourceAgnostic):
    extensions = '.dcm',

    def _match_value(self, value):
        return isinstance(value, pydicom.Dataset)

    def load(self, source: Union[PathLike, BinaryIO], hint: MaybeHint, params) -> Any:
        return pydicom.dcmread(source)

    def save(self, value: Any, destination: Union[PathLike, BinaryIO], hint: MaybeHint, params) -> Hint:
        pydicom.dcmwrite(destination, value)
        return '.dcm'


try:
    import pydicom

    REGISTRY.append(DICOM())
    REGISTRY.append(Gzip(DICOM()))

except ImportError:
    pass
