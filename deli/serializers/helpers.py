from abc import ABC, abstractmethod
from os import PathLike
from typing import Any, Union, BinaryIO, Tuple

from ..serializer import Serializer, MaybeHint, WrongSerializer, Hint, MaybeSerializer


class NoBuffer(Serializer, ABC):
    def match_load_buffer(self, hint: MaybeHint, allow_lazy: bool, params: dict) -> MaybeSerializer:
        pass

    def load_buffer(self, source: BinaryIO, hint: MaybeHint, allow_lazy: bool, params: dict) -> Any:
        raise WrongSerializer

    match_save_buffer = match_load_buffer
    save_buffer = load_buffer


class NoPath(Serializer, ABC):
    def match_load_path(self, source: PathLike, hint: Hint, params: dict) -> MaybeSerializer:
        pass

    def load_path(self, source: PathLike, hint: Hint, params: dict) -> Any:
        raise WrongSerializer

    match_save_path = match_load_path
    save_path = load_path


class PathAsBuffer(Serializer, ABC):
    def match_load_path(self, source: PathLike, hint: Hint, params: dict) -> MaybeSerializer:
        return self.match_load_buffer(hint, False, params)

    def load_path(self, source: PathLike, hint: Hint, params: dict) -> Any:
        with open(source, 'rb') as buffer:
            return self.load_buffer(buffer, hint, False, params)

    def match_save_path(self, value: Any, destination: PathLike, hint: Hint, params: dict) -> MaybeSerializer:
        return self.match_save_buffer(value, hint, params)

    def save_path(self, value: Any, destination: PathLike, hint: Hint, params: dict) -> Hint:
        with open(destination, 'wb') as buffer:
            return self.save_buffer(value, buffer, hint, params)


class SourceAgnostic(Serializer, ABC):
    @abstractmethod
    def load(self, source: Union[PathLike, BinaryIO], hint: MaybeHint, params) -> Any:
        pass

    def load_path(self, source: PathLike, hint: Hint, params: dict) -> Any:
        return self.load(source, hint, params)

    def load_buffer(self, source: BinaryIO, hint: MaybeHint, allow_lazy: bool, params: dict) -> Any:
        return self.load(source, hint, params)

    @abstractmethod
    def save(self, value: Any, destination: Union[PathLike, BinaryIO], hint: MaybeHint, params) -> Hint:
        pass

    def save_path(self, value: Any, destination: PathLike, hint: Hint, params: dict) -> Hint:
        return self.save(value, destination, hint, params)

    def save_buffer(self, value: Any, destination: BinaryIO, hint: MaybeHint, params: dict) -> Hint:
        return self.save(value, destination, hint, params)


class ExtensionMatch(Serializer, ABC):
    extensions: Tuple[str]

    def _match_name(self, name):
        return name is not None and any(name.endswith(x) for x in self.extensions)

    def _match_value(self, value):
        return True

    def _match_load_params(self, params: dict):
        return not params

    def _match_save_params(self, params: dict):
        return not params

    def match_save_buffer(self, value: Any, hint: MaybeHint, params: dict) -> MaybeSerializer:
        return self._match_save(value, hint, params)

    def match_save_path(self, value: Any, destination: PathLike, hint: Hint, params: dict) -> MaybeSerializer:
        return self._match_save(value, hint, params)

    def match_load_path(self, source: PathLike, hint: Hint, params: dict) -> MaybeSerializer:
        return self._match_load(hint, params)

    def match_load_buffer(self, hint: MaybeHint, allow_lazy: bool, params: dict) -> MaybeSerializer:
        return self._match_load(hint, params)

    def _match_save(self, value, hint, params):
        if not self._match_save_params(params):
            return
        if not self._match_value(value):
            return
        if not self._match_name(hint):
            return
        return self

    def _match_load(self, hint, params):
        if not self._match_load_params(params):
            return
        if not self._match_name(hint):
            return
        return self
