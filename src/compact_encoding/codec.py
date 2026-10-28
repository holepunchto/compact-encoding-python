from typing import Protocol, TypeVar

from .state import State

T = TypeVar("T")


class Codec(Protocol[T]):
    """A codec of values of type ``T``, measured with ``preencode()`` before
    being written with ``encode()`` and read back with ``decode()``."""

    def preencode(self, state: State, value: T) -> None: ...

    def encode(self, state: State, value: T) -> None: ...

    def decode(self, state: State) -> T: ...


class CompactError(Exception):
    """Raised for data that can't be decoded."""


class OutOfBounds(CompactError):
    """Raised for a decode that reads past the end of the buffer."""


def encode(codec, value):
    """Encode ``value`` with ``codec`` and return the bytes."""
    state = State()
    codec.preencode(state, value)
    state.allocate()
    codec.encode(state, value)
    return bytes(state.buffer)


def decode(codec, data):
    """Decode a value from ``data`` with ``codec``."""
    state = State(data)
    return codec.decode(state)
