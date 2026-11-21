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


def test_float32_overflows_to_an_infinity():
    # A value the width cannot reach becomes an infinity rather than a refusal:
    # a float codec refuses no number it is given.
    assert cenc.encode(cenc.float32, 4e38).hex() == "0000807f"
    assert cenc.encode(cenc.float32, 1e39).hex() == "0000807f"
    assert cenc.encode(cenc.float32, -4e38).hex() == "000080ff"


def test_float32_rounds_before_it_overflows():
    # The rounding comes first, so a value above the largest binary32 holds is
    # written as that largest one where it rounds down to it, and becomes an
    # infinity only where it rounds past it. A codec comparing against the
    # largest finite value before rounding answers an infinity for both.
    assert cenc.encode(cenc.float32, 3.4028235e38).hex() == "ffff7f7f"
    assert cenc.encode(cenc.float32, 3.4028236e38).hex() == "0000807f"
