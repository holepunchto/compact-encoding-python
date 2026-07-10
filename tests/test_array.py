import pytest

import compact_encoding as cenc
from compact_encoding.codec import CompactError, OutOfBounds

# array(uint): uint(len) prefix + each element inline.
#   []       -> 00
#   [5]      -> 01 05
#   [5, 300] -> 02 05 fd2c01   (uint(300) = fd2c01)
ARRAY_UINT_CASES = [
    ([], "00"),
    ([5], "0105"),
    ([5, 300], "0205fd2c01"),
]


@pytest.mark.parametrize("value,hexbytes", ARRAY_UINT_CASES)
def test_array_uint_encode(value, hexbytes):
    assert cenc.encode(cenc.array(cenc.uint), value).hex() == hexbytes


@pytest.mark.parametrize("value,hexbytes", ARRAY_UINT_CASES)
def test_array_uint_decode(value, hexbytes):
    assert cenc.decode(cenc.array(cenc.uint), bytes.fromhex(hexbytes)) == value


def test_array_string_encode_decode():
    # ["hi"] -> len 01 + string "hi" (uint 02 + 6869)
    codec = cenc.array(cenc.string)
    assert cenc.encode(codec, ["hi"]).hex() == "01026869"
    assert cenc.decode(codec, bytes.fromhex("01026869")) == ["hi"]


def test_array_too_big_guard_raises():
    # Length prefix fe01001000 decodes to uint 0x100001 = 1048577 > 0x100000,
    # so the guard fires before any element is read.
    with pytest.raises(CompactError):
        cenc.decode(cenc.array(cenc.uint), bytes.fromhex("fe01001000"))


def test_array_truncated_element_raises():
    # Declares 5 elements (0x05, well under the size guard), only 1 uint byte
    # present -> the inner uint over-read raises OutOfBounds.
    with pytest.raises(OutOfBounds):
        cenc.decode(cenc.array(cenc.uint), bytes.fromhex("0501"))
