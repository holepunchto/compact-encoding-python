"""A small binary wire codec, wire-compatible with the JS reference."""

from .codec import Codec, CompactError, OutOfBounds, decode, encode
from .integer import int_codec as int
from .integer import uint, uint32
from .state import State

__all__ = [
    "Codec",
    "CompactError",
    "OutOfBounds",
    "State",
    "decode",
    "encode",
    "int",
    "uint",
    "uint32",
]
