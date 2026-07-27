from . import integer
from .state import State


class _Frame:
    def __init__(self, codec):
        self._codec = codec

    def preencode(self, state, m):
        end = state.end
        self._codec.preencode(state, m)
        integer.uint.preencode(state, state.end - end)

    def encode(self, state, m):
        dummy = State()
        self._codec.preencode(dummy, m)
        integer.uint.encode(state, dummy.end)
        self._codec.encode(state, m)

    def decode(self, state):
        outer_end = state.end
        length = integer.uint.decode(state)
        frame_end = state.start + length
        state.end = frame_end
        try:
            m = self._codec.decode(state)
        finally:
            state.end = outer_end
        state.start = frame_end
        return m


def frame(codec):
    return _Frame(codec)
