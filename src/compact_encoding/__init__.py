"""A small binary wire codec, wire-compatible with the JS reference."""

from .bool import bool_codec as bool
from .buffer import buffer
from .codec import Codec, CompactError, OutOfBounds, decode, encode
from .integer import int_codec as int
from .integer import uint, uint32
from .state import State
from .string import utf8
from .string import utf8 as string

__all__ = [
    "Codec",
    "CompactError",
    "OutOfBounds",
    "State",
    "bool",
    "buffer",
    "decode",
    "encode",
    "int",
    "string",
    "uint",
    "uint32",
    "utf8",
]
