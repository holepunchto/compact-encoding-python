from . import integer
from .codec import CompactError


class _Array:
    def __init__(self, codec):
        self._codec = codec

    def preencode(self, state, values):
        integer.uint.preencode(state, len(values))
        for item in values:
            self._codec.preencode(state, item)

    def encode(self, state, values):
        integer.uint.encode(state, len(values))
        for item in values:
            self._codec.encode(state, item)

    def decode(self, state):
        n = integer.uint.decode(state)
        if n > 0x100000:
            raise CompactError("Array is too big")
        return [self._codec.decode(state) for _ in range(n)]


def array(codec):
    return _Array(codec)
