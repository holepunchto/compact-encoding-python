from . import integer
from .codec import OutOfBounds


class _Buffer:
    def preencode(self, state, b):
        integer.uint.preencode(state, len(b))
        state.end += len(b)

    def encode(self, state, b):
        integer.uint.encode(state, len(b))
        n = len(b)
        start = state.start
        state.buffer[start : start + n] = b
        state.start = start + n

    def decode(self, state):
        n = integer.uint.decode(state)
        if state.remaining < n:
            raise OutOfBounds("Out of bounds")
        start = state.start
        data = bytes(state.buffer[start : start + n])
        state.start = start + n
        return data


buffer = _Buffer()
