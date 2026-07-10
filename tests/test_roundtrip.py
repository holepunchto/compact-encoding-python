import pytest

import compact_encoding as cenc
from compact_encoding.state import State

ROUNDTRIP = [
    (cenc.uint, 0),
    (cenc.uint, 300),
    (cenc.uint, 2**53 - 1),
    (cenc.int, 0),
    (cenc.int, -5),
    (cenc.int, 2**52 - 1),
    (cenc.uint32, 0xDEADBEEF),
    (cenc.uint8, 200),
    (cenc.uint16, 40000),
    (cenc.uint24, 16000000),
    (cenc.uint40, 2**39),
    (cenc.uint48, 2**47),
    (cenc.uint56, 2**52),
    (cenc.int24, -8000000),
    (cenc.int40, 2**38),
    (cenc.int48, -(2**46)),
    (cenc.int56, 2**51),
    (cenc.utf8, "hello 世界"),
    (cenc.bool, True),
    (cenc.bool, False),
    (cenc.buffer, b"\x00\x01\x02\xfe\xff"),
    (cenc.float32, 0.5),
    (cenc.float32, -2.0),
    (cenc.float64, 3.141592653589793),
    (cenc.fixed32, bytes(range(32))),
    (cenc.fixed64, bytes(range(64))),
    (cenc.json, {"a": [1, 2], "b": None}),
    (cenc.frame(cenc.uint), 42),
    (cenc.array(cenc.uint), [1, 2, 3]),
    (cenc.record(cenc.string, cenc.uint), {"a": 1, "b": 2}),
]


@pytest.mark.parametrize("codec,value", ROUNDTRIP)
def test_roundtrip(codec, value):
    assert cenc.decode(codec, cenc.encode(codec, value)) == value


def test_frame_backpatch_via_state():
    # Reserve a uint32(0) prefix, encode a body, then back-patch the total
    # length in place - the pattern bare-rpc-python depends on.
    state = State()
    cenc.uint32.preencode(state, 0)  # frame prefix
    cenc.uint.preencode(state, 7)  # body
    state.allocate()
    cenc.uint32.encode(state, 0)  # placeholder
    cenc.uint.encode(state, 7)
    total = state.start

    state.rewind()  # back to offset 0
    cenc.uint32.encode(state, total)  # overwrite in place

    # prefix now holds the real length; body still decodes
    verify = State(bytes(state.buffer))
    assert cenc.uint32.decode(verify) == total
    assert cenc.uint.decode(verify) == 7
