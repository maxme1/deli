from os import PathLike
from typing import Any, BinaryIO, Sequence

from .. import Hint, MaybeHint
from ..serializer import Serializer, WrongSerializer, RequireLazy, MaybeSerializer


class Choice(Serializer):
    def __init__(self, *choices: Serializer):
        self.choices = choices

    # matching

    def match_save_buffer(self, value: Any, hint: MaybeHint, params: dict) -> MaybeSerializer:
        return self._match(lambda choice: choice.match_save_buffer(value, hint, params))

    def match_save_path(self, value: Any, destination: PathLike, hint: Hint, params: dict) -> MaybeSerializer:
        return self._match(lambda choice: choice.match_save_path(value, destination, hint, params))

    def match_load_buffer(self, hint: MaybeHint, allow_lazy: bool, params: dict) -> MaybeSerializer:
        return self._match(lambda choice: choice.match_load_buffer(hint, allow_lazy, params))

    def match_load_path(self, source: PathLike, hint: Hint, params: dict) -> MaybeSerializer:
        return self._match(lambda choice: choice.match_load_path(source, hint, params))

    # saving

    def save_buffer(self, value: Any, destination: BinaryIO, hint: MaybeHint, params: dict) -> Hint:
        position = destination.tell()
        for choice in self.choices:
            try:
                return choice.save_buffer(value, destination, hint, params)
            except WrongSerializer:
                if position != destination.tell():
                    destination.seek(position)
                    destination.truncate()

        raise WrongSerializer('No serializer was able to save the value')

    def save_path(self, value: Any, destination: PathLike, hint: Hint, params: dict) -> Hint:
        for choice in self.choices:
            try:
                return choice.save_path(value, destination, hint, params)
            except WrongSerializer:
                pass

        raise WrongSerializer('No serializer was able to save the value')

    # loading

    def load_buffer(self, source: BinaryIO, hint: MaybeHint, allow_lazy: bool, params: dict) -> Any:
        requires_lazy = None
        position = source.tell()
        for choice in self.choices:
            try:
                return choice.load_buffer(source, hint, allow_lazy, params)
            except (WrongSerializer, RequireLazy) as e:
                if isinstance(e, RequireLazy):
                    requires_lazy = e

                if position != source.tell():
                    source.seek(position)

        if requires_lazy is not None:
            raise requires_lazy
        raise WrongSerializer('No serializer was able to load the value')

    def load_path(self, source: PathLike, hint: Hint, params: dict) -> Any:
        for choice in self.choices:
            try:
                return choice.load_path(source, hint, params)
            except WrongSerializer:
                pass

        raise WrongSerializer('No serializer was able to load the value')

    # internals

    def _match(self, match):
        results = []
        for choice in self.choices:
            value = match(choice)
            if value is not None:
                results.append(value)

        if not results:
            return None
        return Choice(*results)
