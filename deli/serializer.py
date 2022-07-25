import json
from abc import ABC
from enum import Enum
from gzip import GzipFile
from io import TextIOWrapper
from pathlib import Path
from typing import Any, Union, BinaryIO

Hint = Union[str, None]


class Match(Enum):
    Accept, NotSure, Reject = 0, 1, 2


class Serializer(ABC):
    def match_load(self, name: Hint) -> Match:
        pass

    def match_save(self, value: Any, name: Hint) -> Match:
        pass

    def save(self, value: Any, buffer: BinaryIO, name: Hint):
        pass

    def load(self, buffer: BinaryIO, name: Hint) -> Any:
        pass


class WrongSerializer(Exception):
    pass


class Choice(Serializer):
    def __init__(self, *choices: Serializer):
        self.choices = choices

    @staticmethod
    def _filter(values):
        return [v for k, v in sorted(values, key=lambda m: m[0].value) if k is not Match.Reject]

    def match_load(self, name: Hint) -> Match:
        return min((choice.match_load(name) for choice in self.choices), key=lambda m: m.value, default=Match.Reject)

    def match_save(self, value: Any, name: Hint) -> Match:
        return min(
            (choice.match_save(value, name) for choice in self.choices),
            key=lambda m: m.value, default=Match.Reject
        )

    def load(self, buffer: BinaryIO, name: Hint) -> Any:
        choices = self._filter([(choice.match_load(name), choice) for choice in self.choices])

        position = buffer.tell()
        for choice in choices:
            try:
                return choice.load(buffer, name)
            except WrongSerializer:
                buffer.seek(position)

        raise WrongSerializer(f'No serializer was able to read the value')

    def save(self, value: Any, buffer: BinaryIO, name: Hint):
        choices = self._filter([(choice.match_save(value, name), choice) for choice in self.choices])

        position = buffer.tell()
        for choice in choices:
            try:
                return choice.save(value, buffer, name)
            except WrongSerializer:
                buffer.seek(position)
                buffer.truncate()

        raise WrongSerializer(f'No serializer was able to save the value {value}')


class JSON(Serializer):
    @staticmethod
    def _match(name):
        if name is not None and name.endswith('.json'):
            return Match.Accept
        return Match.NotSure

    def match_save(self, value: Any, name: Hint) -> Match:
        return self._match(name)

    def match_load(self, name: Hint) -> Match:
        return self._match(name)

    def load(self, buffer: BinaryIO, name: Hint) -> Any:
        wrapper = TextIOWrapper(buffer)
        try:
            return json.load(wrapper)
        except TypeError as e:
            raise WrongSerializer from e
        finally:
            wrapper.detach()

    def save(self, value: Any, buffer: BinaryIO, name: Hint):
        wrapper = TextIOWrapper(buffer)
        try:
            json.dump(value, wrapper)
        except TypeError as e:
            raise WrongSerializer from e
        finally:
            wrapper.detach()


class GZip(Serializer):
    def __init__(self, serializer: Serializer, compression: int = 1, mtime: Union[float, None] = 0):
        self.mtime = mtime
        self.compression = compression
        self.serializer = serializer
        self._ext = '.gz'

    def _match(self, name):
        return name is not None and name.endswith(self._ext)

    def _trim(self, name):
        return None if name is None else name[:-len(self._ext)]

    def match_save(self, value: Any, name: Hint) -> Match:
        if not self._match(name):
            return Match.NotSure
        return self.serializer.match_save(value, self._trim(name))

    def match_load(self, name: Hint) -> Match:
        if not self._match(name):
            return Match.NotSure
        return self.serializer.match_load(self._trim(name))

    def load(self, buffer: BinaryIO, name: Hint) -> Any:
        with GzipFile(fileobj=buffer, mode='rb') as local:
            return self.serializer.load(local, self._trim(name))

    def save(self, value: Any, buffer: BinaryIO, name: Hint):
        with GzipFile(fileobj=buffer, mode='wb', compresslevel=self.compression, mtime=self.mtime) as local:
            return self.serializer.save(value, local, self._trim(name))


def load(path: Union[str, Path, BinaryIO], hint: Hint = None):
    choice = Choice(
        JSON(),
        GZip(JSON()),
    )

    if isinstance(path, str):
        path = Path(path)
    if isinstance(path, Path):
        if hint is None:
            hint = path.name
        with path.open('rb') as buffer:
            return choice.load(buffer, hint)

    if not isinstance(path, BinaryIO):
        raise TypeError('Need a binary buffer')

    return choice.load(path, hint)


def save(value: Any, path: Union[str, Path, BinaryIO], hint: Hint = None):
    choice = Choice(
        JSON(),
        GZip(JSON()),
    )

    if isinstance(path, str):
        path = Path(path)
    if isinstance(path, Path):
        if hint is None:
            hint = path.name
        with path.open('wb') as buffer:
            return choice.save(value, buffer, hint)

    if not isinstance(path, BinaryIO):
        raise TypeError('Need a binary buffer')

    return choice.save(value, path, hint)
