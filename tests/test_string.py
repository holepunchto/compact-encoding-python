import pytest

import compact_encoding as cenc

STRING_CASES = [
    ("", "00"),
    ("hi", "026869"),
    ("é", "02c3a9"),  # e-acute: 2 UTF-8 bytes
    ("€", "03e282ac"),  # euro sign: 3 UTF-8 bytes
]


@pytest.mark.parametrize("value,hexbytes", STRING_CASES)
def test_utf8_encode(value, hexbytes):
    assert cenc.encode(cenc.utf8, value).hex() == hexbytes


@pytest.mark.parametrize("value,hexbytes", STRING_CASES)
def test_utf8_decode(value, hexbytes):
    assert cenc.decode(cenc.utf8, bytes.fromhex(hexbytes)) == value


def test_string_is_alias_of_utf8():
    assert cenc.string is cenc.utf8


def test_utf8_decode_is_lenient():
    # length 1, then 0xff which is not valid UTF-8 -> U+FFFD replacement
    assert cenc.decode(cenc.utf8, bytes.fromhex("01ff")) == "�"


def test_utf8_decode_truncated_raises():
    from compact_encoding.codec import OutOfBounds

    with pytest.raises(OutOfBounds):
        cenc.decode(cenc.utf8, bytes.fromhex("0568"))  # says 5 bytes, has 1
