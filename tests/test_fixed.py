import pytest

import compact_encoding as cenc

BUF32 = bytes(range(32))
BUF64 = bytes(range(64))


def test_fixed32_encode_decode():
    encoded = cenc.encode(cenc.fixed32, BUF32)
    assert encoded == BUF32  # no length prefix, raw bytes
    assert cenc.decode(cenc.fixed32, encoded) == BUF32


def test_fixed64_encode_decode():
    encoded = cenc.encode(cenc.fixed64, BUF64)
    assert encoded == BUF64
    assert cenc.decode(cenc.fixed64, encoded) == BUF64


def test_fixed_decode_returns_a_copy():
    encoded = cenc.encode(cenc.fixed32, BUF32)
    out = cenc.decode(cenc.fixed32, encoded)
    assert isinstance(out, bytes)  # a copy, not a view into the buffer


def test_fixed_rejects_wrong_length_via_oneshot():
    with pytest.raises(ValueError):
        cenc.encode(cenc.fixed32, bytes(31))
    with pytest.raises(ValueError):
        cenc.encode(cenc.fixed32, bytes(33))


def test_fixed_rejects_wrong_length_via_direct_encode():
    from compact_encoding.state import State

    state = State()
    state.buffer = bytearray(32)
    with pytest.raises(ValueError):
        cenc.fixed32.encode(
            state, bytes(31)
        )  # encode must validate, not silently resize


def test_fixed_decode_truncated_raises():
    from compact_encoding.codec import OutOfBounds

    with pytest.raises(OutOfBounds):
        cenc.decode(cenc.fixed32, bytes(31))  # fewer than 32 bytes
