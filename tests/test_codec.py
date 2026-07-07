from compact_encoding.codec import CompactError, OutOfBounds, decode, encode


class _OneByte:
    """Stub codec: encodes an int 0-255 as a single byte."""

    def preencode(self, state, value):
        state.end += 1

    def encode(self, state, value):
        state.buffer[state.start] = value
        state.start += 1

    def decode(self, state):
        v = state.buffer[state.start]
        state.start += 1
        return v


def test_out_of_bounds_is_a_compact_error():
    assert issubclass(OutOfBounds, CompactError)


def test_encode_helper_returns_bytes():
    result = encode(_OneByte(), 42)
    assert result == b"\x2a"
    assert isinstance(result, bytes)


def test_decode_helper_reads_value():
    assert decode(_OneByte(), b"\x2a") == 42


def test_roundtrip_via_helpers():
    codec = _OneByte()
    assert decode(codec, encode(codec, 7)) == 7
