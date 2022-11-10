from os import PathLike
from typing import Any, BinaryIO, Sequence

from .. import Hint, MatchHint, MaybeHint
from ..serializer import Serializer, WrongSerializer, RequireLazy


class Choice(Serializer):
    def __init__(self, *choices: Serializer):
        self.choices = choices

    # matching

    def match_save_buffer(self, value: Any, hint: MaybeHint, params: dict) -> MatchHint:
        return min(
            (choice.match_save_buffer(value, hint, params) for choice in self.choices),
            key=lambda m: m.value, default=MatchHint.Reject
        )

    def match_save_path(self, value: Any, destination: PathLike, hint: Hint, params: dict) -> MatchHint:
        return min(
            (choice.match_save_path(value, destination, hint, params) for choice in self.choices),
            key=lambda m: m.value, default=MatchHint.Reject
        )

    def match_load_buffer(self, hint: MaybeHint, allow_lazy: bool, params: dict) -> MatchHint:
        return min(
            (choice.match_load_buffer(hint, allow_lazy, params) for choice in self.choices),
            key=lambda m: m.value, default=MatchHint.Reject
        )

    def match_load_path(self, source: PathLike, hint: Hint, params: dict) -> MatchHint:
        return min(
            (choice.match_load_path(source, hint, params) for choice in self.choices),
            key=lambda m: m.value, default=MatchHint.Reject
        )

    # saving

    def save_buffer(self, value: Any, destination: BinaryIO, hint: MaybeHint, params: dict) -> Hint:
        choices = self._filter(
            (choice.match_save_buffer(value, hint, params), choice)
            for choice in self.choices
        )

        position = destination.tell()
        for choice in choices:
            try:
                return choice.save_buffer(value, destination, hint, params)
            except WrongSerializer:
                if position != destination.tell():
                    destination.seek(position)
                    destination.truncate()

        raise WrongSerializer('No serializer was able to save the value')

    def save_path(self, value: Any, destination: PathLike, hint: Hint, params: dict) -> Hint:
        choices = self._filter(
            (choice.match_save_path(value, destination, hint, params), choice)
            for choice in self.choices
        )

        for choice in choices:
            try:
                return choice.save_path(value, destination, hint, params)
            except WrongSerializer:
                pass

        raise WrongSerializer('No serializer was able to save the value')

    # loading

    def load_buffer(self, source: BinaryIO, hint: MaybeHint, allow_lazy: bool, params: dict) -> Any:
        choices = self._filter(
            (choice.match_load_buffer(hint, allow_lazy, params), choice)
            for choice in self.choices
        )

        requires_lazy = None
        position = source.tell()
        for choice in choices:
            try:
                return choice.load_buffer(source, hint, allow_lazy, params)
            except (WrongSerializer, RequireLazy) as e:
                if isinstance(e, RequireLazy):
                    requires_lazy = e

                if position != source.tell():
                    source.seek(position)
                    source.truncate()

        if requires_lazy is not None:
            raise requires_lazy
        raise WrongSerializer('No serializer was able to save the value')

    def load_path(self, source: PathLike, hint: Hint, params: dict) -> Any:
        choices = self._filter(
            (choice.match_load_path(source, hint, params), choice)
            for choice in self.choices
        )

        for choice in choices:
            try:
                return choice.load_path(source, hint, params)
            except WrongSerializer:
                pass

        raise WrongSerializer('No serializer was able to save the value')

    # internals

    @staticmethod
    def _filter(values) -> Sequence[Serializer]:
        return [v for k, v in sorted(values, key=lambda m: m[0].value) if k is not MatchHint.Reject]
