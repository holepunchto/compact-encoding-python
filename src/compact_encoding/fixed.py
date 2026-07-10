from .codec import OutOfBounds


class _Fixed:
    def __init__(self, n):
        self._n = n

    def preencode(self, state, s):
        if len(s) != self._n:
            raise ValueError("Incorrect buffer size")
        state.end += self._n

    def encode(self, state, s):
        if len(s) != self._n:
            raise ValueError("Incorrect buffer size")
        start = state.start
        state.buffer[start : start + self._n] = s
        state.start = start + self._n

    def decode(self, state):
        if state.remaining < self._n:
            raise OutOfBounds("Out of bounds")
        start = state.start
        value = bytes(state.buffer[start : start + self._n])
        state.start = start + self._n
        return value


def fixed(n):
    return _Fixed(n)


fixed32 = fixed(32)
fixed64 = fixed(64)
