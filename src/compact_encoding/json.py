import json as _json

from .string import utf8


def _dumps(v):
    return _json.dumps(v, separators=(",", ":"), ensure_ascii=False)


class _Json:
    def preencode(self, state, v):
        utf8.preencode(state, _dumps(v))

    def encode(self, state, v):
        utf8.encode(state, _dumps(v))

    def decode(self, state):
        return _json.loads(utf8.decode(state))


json_codec = _Json()
