from os import PathLike
from typing import BinaryIO, Any, Union

from ..serializer import MaybeHint, REGISTRY, Hint, WrongSerializer
from .helpers import ExtensionMatch, SourceAgnostic
from .packaged import Gzip


class CSV(ExtensionMatch, SourceAgnostic):
    extensions = '.csv',

    def _match_value(self, value):
        return isinstance(value, (DataFrame, Series))

    def _match_save_params(self, params: dict):
        return set(params) <= {'index'}

    def load(self, source: Union[PathLike, BinaryIO], hint: MaybeHint, params) -> Any:
        try:
            return pd.read_csv(source)
        except pd.errors.EmptyDataError as e:
            if hint is not None:
                raise
            raise WrongSerializer from e

    def save(self, value: Any, destination: Union[PathLike, BinaryIO], hint: MaybeHint, params) -> Hint:
        value.to_csv(destination, **params)
        return '.csv'


try:
    import pandas as pd
    from pandas import DataFrame, Series

    REGISTRY.append(CSV())
    REGISTRY.append(Gzip(CSV()))

except ImportError:
    pass
