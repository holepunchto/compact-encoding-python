from . import integer
from .codec import OutOfBounds


class _Utf8:
    def preencode(self, state, s):
        data = s.encode("utf-8")
        integer.uint.preencode(state, len(data))
        state.end += len(data)

    def encode(self, state, s):
        data = s.encode("utf-8")
        integer.uint.encode(state, len(data))
        n = len(data)
        start = state.start
        state.buffer[start : start + n] = data
        state.start = start + n

    def decode(self, state):
        n = integer.uint.decode(state)
        if state.remaining < n:
            raise OutOfBounds("Out of bounds")
        start = state.start
        data = state.buffer[start : start + n]
        state.start = start + n
        return bytes(data).decode("utf-8", errors="replace")


utf8 = _Utf8()
