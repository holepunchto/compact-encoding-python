from . import integer


class _Record:
    def __init__(self, key_codec, value_codec):
        self._key = key_codec
        self._value = value_codec

    def preencode(self, state, v):
        integer.uint.preencode(state, len(v))
        for k, value in v.items():
            self._key.preencode(state, k)
            self._value.preencode(state, value)

    def encode(self, state, v):
        integer.uint.encode(state, len(v))
        for k, value in v.items():
            self._key.encode(state, k)
            self._value.encode(state, value)

    def decode(self, state):
        n = integer.uint.decode(state)
        out = {}
        for _ in range(n):
            key = self._key.decode(state)
            out[key] = self._value.decode(state)
        return out


def record(key_codec, value_codec):
    return _Record(key_codec, value_codec)
