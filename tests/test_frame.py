import pytest

import compact_encoding as cenc
from compact_encoding.codec import OutOfBounds

# frame(uint): uint(len) prefix + inner uint bytes.
#   5   -> inner uint(5)   = 05        (1 byte) -> len 01 -> 0105
#   0   -> inner uint(0)   = 00        (1 byte) -> len 01 -> 0100
#   300 -> inner uint(300) = fd2c01    (3 bytes) -> len 03 -> 03fd2c01
FRAME_UINT_CASES = [
    (5, "0105"),
    (0, "0100"),
    (300, "03fd2c01"),
]


@pytest.mark.parametrize("value,hexbytes", FRAME_UINT_CASES)
def test_frame_uint_encode(value, hexbytes):
    assert cenc.encode(cenc.frame(cenc.uint), value).hex() == hexbytes


@pytest.mark.parametrize("value,hexbytes", FRAME_UINT_CASES)
def test_frame_uint_decode(value, hexbytes):
    assert cenc.decode(cenc.frame(cenc.uint), bytes.fromhex(hexbytes)) == value


def test_frame_buffer_matches_length_prefix():
    # A framed buffer is a length prefix around c.buffer's own bytes: the
    # frame length equals the full inner encoding (uint-len + raw bytes).
    payload = b"\x01\x02\x03"
    inner = cenc.encode(cenc.buffer, payload)  # 03010203 (4 bytes)
    framed = cenc.encode(cenc.frame(cenc.buffer), payload)
    assert framed.hex() == "04" + inner.hex()  # len 04 + 03010203
    assert cenc.decode(cenc.frame(cenc.buffer), framed) == payload


def test_frame_restores_cursor_for_following_field():
    # Encode a framed value then a plain uint; both must decode back in order,
    # proving decode restores state.end and leaves state.start after the frame.
    from compact_encoding.state import State

    fr = cenc.frame(cenc.uint)
    state = State()
    fr.preencode(state, 300)
    cenc.uint.preencode(state, 42)
    state.allocate()
    fr.encode(state, 300)
    cenc.uint.encode(state, 42)

    verify = State(bytes(state.buffer))
    assert fr.decode(verify) == 300
    assert cenc.uint.decode(verify) == 42


def test_frame_decode_restores_end_on_inner_error():
    # Inner uint over-reads past the frame boundary and raises; state.end must
    # be restored to the outer end so the State is not left corrupted. Trailing
    # bytes make the outer end (5) larger than the frame end (2), so a missing
    # restore is observable.
    from compact_encoding.state import State

    state = State(bytes.fromhex("01fd000099"))
    outer_end = state.end
    with pytest.raises(OutOfBounds):
        cenc.frame(cenc.uint).decode(state)
    assert state.end == outer_end


def test_frame_decode_truncated_raises():
    # Inner uint's continuation byte (0xfd) demands 2 more bytes that
    # aren't present; verified this also raises against the JS reference.
    with pytest.raises(OutOfBounds):
        cenc.decode(cenc.frame(cenc.uint), bytes.fromhex("01fd"))
