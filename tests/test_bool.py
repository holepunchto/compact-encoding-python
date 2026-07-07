import pytest

import compact_encoding as cenc


def test_bool_encode_true():
    assert cenc.encode(cenc.bool, True).hex() == "01"


def test_bool_encode_false():
    assert cenc.encode(cenc.bool, False).hex() == "00"


def test_bool_decode():
    assert cenc.decode(cenc.bool, b"\x01") is True
    assert cenc.decode(cenc.bool, b"\x00") is False


def test_bool_decode_nonone_byte_is_false():
    assert cenc.decode(cenc.bool, b"\x02") is False


def test_bool_decode_empty_raises():
    from compact_encoding.codec import OutOfBounds

    with pytest.raises(OutOfBounds):
        cenc.decode(cenc.bool, b"")
