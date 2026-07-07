from .codec import OutOfBounds


class _Bool:
    def preencode(self, state, b):
        state.end += 1

    def encode(self, state, b):
        state.buffer[state.start] = 1 if b else 0
        state.start += 1

    def decode(self, state):
        if state.remaining < 1:
            raise OutOfBounds("Out of bounds")
        v = state.buffer[state.start]
        state.start += 1
        return v == 1


bool_codec = _Bool()
