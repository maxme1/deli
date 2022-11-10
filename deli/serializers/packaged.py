import json
import pickle
from gzip import GzipFile, BadGzipFile
from io import TextIOWrapper
from typing import Any, BinaryIO

from .helpers import ExtensionMatch, NoPath
from ..serializer import Serializer, MatchHint, MaybeHint, WrongSerializer, REGISTRY, Hint


class JSON(NoPath, ExtensionMatch):
    extensions = '.json',

    def _match_save_params(self, params: dict):
        return set(params) <= {'indent'}

    def load_buffer(self, source: BinaryIO, hint: MaybeHint, allow_lazy: bool, params: dict) -> Any:
        wrapper = TextIOWrapper(source)
        try:
            return json.load(wrapper)
        except TypeError as e:
            raise WrongSerializer from e
        finally:
            wrapper.detach()

    def save_buffer(self, value: Any, destination: BinaryIO, hint: MaybeHint, params: dict) -> Hint:
        wrapper = TextIOWrapper(destination)
        try:
            json.dump(value, wrapper, **params)
        except TypeError as e:
            raise WrongSerializer from e
        finally:
            wrapper.detach()

        return '.json'


class Pickle(ExtensionMatch, NoPath):
    extensions = '.pkl',

    # TODO: check magic bits
    def load_buffer(self, source: BinaryIO, hint: MaybeHint, allow_lazy: bool, params: dict) -> Any:
        return pickle.load(source)

    def save_buffer(self, value: Any, destination: BinaryIO, hint: MaybeHint, params: dict) -> Hint:
        pickle.dump(value, destination)
        return '.pkl'


class Text(ExtensionMatch, NoPath):
    extensions = '.txt',

    def _match_value(self, value):
        return isinstance(value, str)

    def load_buffer(self, source: BinaryIO, hint: MaybeHint, allow_lazy: bool, params: dict) -> Any:
        wrapper = TextIOWrapper(source)
        try:
            return wrapper.read()
        finally:
            wrapper.detach()

    def save_buffer(self, value: Any, destination: BinaryIO, hint: MaybeHint, params: dict) -> Hint:
        wrapper = TextIOWrapper(destination)
        try:
            wrapper.write(value)
        finally:
            wrapper.detach()

        return '.txt'


class Gzip(NoPath, Serializer):
    def __init__(self, serializer: Serializer):
        self.serializer = serializer
        self._ext = '.gz'

    def _match(self, name):
        return name is not None and name.endswith(self._ext)

    def _trim(self, name):
        return None if name is None else name[:-len(self._ext)]

    def match_save_buffer(self, value: Any, hint: MaybeHint, params: dict) -> MatchHint:
        if not self._match(hint):
            return MatchHint.NotSure

        params = params.copy()
        params.pop('compression', None)
        return self.serializer.match_save_buffer(value, self._trim(hint), params)

    def match_load_buffer(self, hint: MaybeHint, allow_lazy: bool, params: dict) -> MatchHint:
        if not self._match(hint):
            return MatchHint.NotSure

        return self.serializer.match_load_buffer(self._trim(hint), allow_lazy, params)

    def load_buffer(self, source: BinaryIO, hint: MaybeHint, allow_lazy: bool, params: dict) -> Any:
        try:
            with GzipFile(fileobj=source, mode='rb') as local:
                return self.serializer.load_buffer(local, self._trim(hint), allow_lazy, params)
        except BadGzipFile as e:
            raise WrongSerializer from e

    def save_buffer(self, value: Any, destination: BinaryIO, hint: MaybeHint, params: dict) -> Hint:
        params = params.copy()
        compression = params.pop('compression', 1)
        mtime = 0

        try:
            with GzipFile(fileobj=destination, mode='wb', compresslevel=compression, mtime=mtime) as local:
                result = self.serializer.save_buffer(value, local, self._trim(hint), params)
        except BadGzipFile as e:
            raise WrongSerializer from e

        return result + self._ext


REGISTRY.extend((
    JSON(), Text(), Pickle(),
))
