import pytest

import compact_encoding as cenc

FLOAT32_CASES = [
    (0.5, "0000003f"),
    (1.5, "0000c03f"),
    (-2.0, "000000c0"),
]

FLOAT64_CASES = [
    (0.5, "000000000000e03f"),
    (1.5, "000000000000f83f"),
    (-2.0, "00000000000000c0"),
]


@pytest.mark.parametrize("value,hexbytes", FLOAT32_CASES)
def test_float32(value, hexbytes):
    assert cenc.encode(cenc.float32, value).hex() == hexbytes
    assert cenc.decode(cenc.float32, bytes.fromhex(hexbytes)) == value


@pytest.mark.parametrize("value,hexbytes", FLOAT64_CASES)
def test_float64(value, hexbytes):
    assert cenc.encode(cenc.float64, value).hex() == hexbytes
    assert cenc.decode(cenc.float64, bytes.fromhex(hexbytes)) == value


def test_float_decode_truncated_raises():
    from compact_encoding.codec import OutOfBounds

    with pytest.raises(OutOfBounds):
        cenc.decode(cenc.float32, bytes.fromhex("010203"))  # 3 of 4
    with pytest.raises(OutOfBounds):
        cenc.decode(cenc.float64, bytes.fromhex("01020304050607"))  # 7 of 8
