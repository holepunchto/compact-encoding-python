import pytest

import compact_encoding as cenc

BUFFER_CASES = [
    (b"", "00"),
    (b"\x01\x02\x03", "03010203"),
    (b"\xff" * 4, "04ffffffff"),
]


@pytest.mark.parametrize("value,hexbytes", BUFFER_CASES)
def test_buffer_encode(value, hexbytes):
    assert cenc.encode(cenc.buffer, value).hex() == hexbytes


@pytest.mark.parametrize("value,hexbytes", BUFFER_CASES)
def test_buffer_decode(value, hexbytes):
    result = cenc.decode(cenc.buffer, bytes.fromhex(hexbytes))
    assert result == value
    assert isinstance(result, bytes)


def test_buffer_decode_returns_a_copy():
    src = bytearray.fromhex("03010203")
    result = cenc.decode(cenc.buffer, src)
    src[1] = 0x99  # mutate the source after decode
    assert result == b"\x01\x02\x03"  # copy is unaffected


def test_buffer_encode_accepts_bytearray():
    assert cenc.encode(cenc.buffer, bytearray(b"\x01\x02")).hex() == "020102"


def test_buffer_decode_truncated_raises():
    from compact_encoding.codec import OutOfBounds

    with pytest.raises(OutOfBounds):
        cenc.decode(cenc.buffer, bytes.fromhex("0501"))  # says 5, has 1
