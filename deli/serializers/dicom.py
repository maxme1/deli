from os import PathLike
from typing import BinaryIO, Any, Union

from ..serializer import MaybeHint, REGISTRY, Hint, WrongSerializer
from .helpers import ExtensionMatch, SourceAgnostic
from .packaged import Gzip


class DICOM(ExtensionMatch, SourceAgnostic):
    extensions = '.dcm',

    def _match_value(self, value):
        return isinstance(value, pydicom.Dataset)

    def load(self, source: Union[PathLike, BinaryIO], hint: MaybeHint, params) -> Any:
        try:
            return pydicom.dcmread(source)
        except pydicom.errors.InvalidDicomError as e:
            if hint is not None:
                raise
            raise WrongSerializer from e

    def save(self, value: Any, destination: Union[PathLike, BinaryIO], hint: MaybeHint, params) -> Hint:
        pydicom.dcmwrite(destination, value)
        return '.dcm'


try:
    import pydicom
    import pydicom.errors

    REGISTRY.append(DICOM())
    REGISTRY.append(Gzip(DICOM()))

except ImportError:
    pass
