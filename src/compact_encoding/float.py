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
        state.buffer[s : s + self._n] = struct.pack(self._fmt, n)
        state.start = s + self._n

    def decode(self, state):
        if state.remaining < self._n:
            raise OutOfBounds("Out of bounds")
        s = state.start
        value = struct.unpack(self._fmt, state.buffer[s : s + self._n])[0]
        state.start = s + self._n
        return value


float32 = _Float("<f", 4)
float64 = _Float("<d", 8)
