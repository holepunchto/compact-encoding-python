import math
import struct

from .codec import OutOfBounds


class _Float:
    def __init__(self, fmt, nbytes):
        self._fmt = fmt
        self._n = nbytes

    def preencode(self, state, n):
        state.end += self._n

    def encode(self, state, n):
        s = state.start
        state.buffer[s : s + self._n] = self._pack(n)
        state.start = s + self._n

    def _pack(self, n):
        try:
            return struct.pack(self._fmt, n)
        except OverflowError:
            return struct.pack(self._fmt, math.copysign(math.inf, n))

    def decode(self, state):
        if state.remaining < self._n:
            raise OutOfBounds("Out of bounds")
        s = state.start
        value = struct.unpack(self._fmt, state.buffer[s : s + self._n])[0]
        state.start = s + self._n
        return value


float32 = _Float("<f", 4)
float64 = _Float("<d", 8)
