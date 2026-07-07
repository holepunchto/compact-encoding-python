from typing import Protocol, TypeVar

from .state import State

T = TypeVar("T")


class Codec(Protocol[T]):
    def preencode(self, state: State, value: T) -> None: ...

    def encode(self, state: State, value: T) -> None: ...

    def decode(self, state: State) -> T: ...


class CompactError(Exception):
    pass


class OutOfBounds(CompactError):
    pass


def encode(codec, value):
    state = State()
    codec.preencode(state, value)
    state.allocate()
    codec.encode(state, value)
    return bytes(state.buffer)


def decode(codec, data):
    state = State(data)
    return codec.decode(state)
