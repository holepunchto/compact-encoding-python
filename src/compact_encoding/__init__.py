"""A small binary wire codec, wire-compatible with the JS reference."""

from .bool import bool_codec as bool
from .buffer import buffer
from .codec import Codec, CompactError, OutOfBounds, decode, encode
from .fixed import fixed, fixed32, fixed64
from .float import float32, float64
from .integer import (
    int24,
    int40,
    int48,
    int56,
    uint,
    uint8,
    uint16,
    uint24,
    uint32,
    uint40,
    uint48,
    uint56,
)
from .integer import int_codec as int
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
    "fixed",
    "fixed32",
    "fixed64",
    "float32",
    "float64",
    "int",
    "int24",
    "int40",
    "int48",
    "int56",
    "string",
    "uint",
    "uint8",
    "uint16",
    "uint24",
    "uint32",
    "uint40",
    "uint48",
    "uint56",
    "utf8",
]
