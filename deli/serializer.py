from abc import ABC, abstractmethod
from enum import Enum
from os import PathLike
from pathlib import Path
from typing import Any, Union, BinaryIO

Hint = str
MaybeHint = Union[str, None]
MaybePath = Union[Path, None]
REGISTRY = []


class MatchHint(Enum):
    Accept, NotSure, Reject = 0, 1, 2


class Serializer(ABC):
    # save
    @abstractmethod
    def match_save_buffer(self, value: Any, hint: MaybeHint, params: dict) -> MatchHint:
        pass

    @abstractmethod
    def save_buffer(self, value: Any, destination: BinaryIO, hint: MaybeHint, params: dict) -> Hint:
        pass

    @abstractmethod
    def match_save_path(self, value: Any, destination: PathLike, hint: Hint, params: dict) -> MatchHint:
        pass

    @abstractmethod
    def save_path(self, value: Any, destination: PathLike, hint: Hint, params: dict) -> Hint:
        pass

    # load
    @abstractmethod
    def match_load_buffer(self, hint: MaybeHint, allow_lazy: bool, params: dict) -> MatchHint:
        pass

    @abstractmethod
    def load_buffer(self, source: BinaryIO, hint: MaybeHint, allow_lazy: bool, params: dict) -> Any:
        pass

    @abstractmethod
    def match_load_path(self, source: PathLike, hint: Hint, params: dict) -> MatchHint:
        pass

    @abstractmethod
    def load_path(self, source: PathLike, hint: Hint, params: dict) -> Any:
        pass


class WrongSerializer(Exception):
    pass


class RequireLazy(Exception):
    pass
