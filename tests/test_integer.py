import pytest

import compact_encoding as cenc

MAX_SAFE = 2**53 - 1

UINT_CASES = [
    (0, "00"),
    (1, "01"),
    (0xFC, "fc"),
    (0xFD, "fdfd00"),
    (0xFF, "fdff00"),
    (0xFFFF, "fdffff"),
    (0x10000, "fe00000100"),
    (0xFFFFFFFF, "feffffffff"),
    (0x100000000, "ff0000000001000000"),
    (MAX_SAFE, "ffffffffffffff1f00"),
]


@pytest.mark.parametrize("value,hexbytes", UINT_CASES)
def test_uint_encode(value, hexbytes):
    assert cenc.encode(cenc.uint, value).hex() == hexbytes


@pytest.mark.parametrize("value,hexbytes", UINT_CASES)
def test_uint_decode(value, hexbytes):
    assert cenc.decode(cenc.uint, bytes.fromhex(hexbytes)) == value


def test_uint_rejects_negative():
    with pytest.raises(ValueError):
        cenc.encode(cenc.uint, -1)


def test_uint_rejects_beyond_max_safe_integer():
    with pytest.raises(ValueError):
        cenc.encode(cenc.uint, MAX_SAFE + 1)


def test_uint_decode_truncated_varint_raises():
    from compact_encoding.codec import OutOfBounds

    with pytest.raises(OutOfBounds):
        cenc.decode(cenc.uint, bytes.fromhex("fd01"))  # marker says u16, only 1 byte


def test_uint_decode_empty_raises():
    from compact_encoding.codec import OutOfBounds

    with pytest.raises(OutOfBounds):
        cenc.decode(cenc.uint, b"")


UINT32_CASES = [
    (0, "00000000"),
    (1, "01000000"),
    (0xFFFFFFFF, "ffffffff"),
]


@pytest.mark.parametrize("value,hexbytes", UINT32_CASES)
def test_uint32_encode(value, hexbytes):
    assert cenc.encode(cenc.uint32, value).hex() == hexbytes


@pytest.mark.parametrize("value,hexbytes", UINT32_CASES)
def test_uint32_decode(value, hexbytes):
    assert cenc.decode(cenc.uint32, bytes.fromhex(hexbytes)) == value


def test_uint32_rejects_out_of_range():
    with pytest.raises(ValueError):
        cenc.encode(cenc.uint32, 0x100000000)
    with pytest.raises(ValueError):
        cenc.encode(cenc.uint32, -1)


def test_uint32_decode_truncated_raises():
    from compact_encoding.codec import OutOfBounds

    with pytest.raises(OutOfBounds):
        cenc.decode(cenc.uint32, bytes.fromhex("010203"))  # only 3 of 4 bytes


INT_CASES = [
    (0, "00"),
    (-1, "01"),
    (1, "02"),
    (-2, "03"),
    (2, "04"),
    (63, "7e"),
    (-64, "7f"),
]


@pytest.mark.parametrize("value,hexbytes", INT_CASES)
def test_int_encode(value, hexbytes):
    assert cenc.encode(cenc.int, value).hex() == hexbytes


@pytest.mark.parametrize("value,hexbytes", INT_CASES)
def test_int_decode(value, hexbytes):
    assert cenc.decode(cenc.int, bytes.fromhex(hexbytes)) == value


def test_int_max_positive_roundtrips():
    assert cenc.decode(cenc.int, cenc.encode(cenc.int, 2**52 - 1)) == 2**52 - 1


def test_int_min_negative_roundtrips():
    assert cenc.decode(cenc.int, cenc.encode(cenc.int, -(2**52))) == -(2**52)


def test_int_rejects_beyond_range():
    with pytest.raises(ValueError):
        cenc.encode(cenc.int, 2**52)  # zigzag -> 2**53 > MAX_SAFE
    with pytest.raises(ValueError):
        cenc.encode(cenc.int, -(2**52) - 1)


SIZED_UINT_CASES = [
    ("uint8", 0, "00"),
    ("uint8", 1, "01"),
    ("uint8", 255, "ff"),
    ("uint16", 0, "0000"),
    ("uint16", 1, "0100"),
    ("uint16", 65535, "ffff"),
    ("uint24", 0, "000000"),
    ("uint24", 66051, "030201"),
    ("uint24", 16777215, "ffffff"),
    ("uint40", 0, "0000000000"),
    ("uint40", 1099511627775, "ffffffffff"),
    ("uint48", 0, "000000000000"),
    ("uint48", 4294967295, "ffffffff0000"),
    ("uint48", 281474976710655, "ffffffffffff"),
    ("uint56", 0, "00000000000000"),
    ("uint56", MAX_SAFE, "ffffffffffff1f"),  # MAX_SAFE ceiling binds for uint56
]


@pytest.mark.parametrize("name,value,hexbytes", SIZED_UINT_CASES)
def test_sized_uint_encode(name, value, hexbytes):
    codec = getattr(cenc, name)
    assert cenc.encode(codec, value).hex() == hexbytes


@pytest.mark.parametrize("name,value,hexbytes", SIZED_UINT_CASES)
def test_sized_uint_decode(name, value, hexbytes):
    codec = getattr(cenc, name)
    assert cenc.decode(codec, bytes.fromhex(hexbytes)) == value


@pytest.mark.parametrize(
    "name,bad",
    [
        ("uint8", 256),
        ("uint16", 65536),
        ("uint24", 16777216),
        ("uint40", 2**40),
        ("uint48", 2**48),
        ("uint56", 2**53),  # exceeds MAX_SAFE_INTEGER
        ("uint8", -1),
    ],
)
def test_sized_uint_rejects_out_of_range(name, bad):
    with pytest.raises(ValueError):
        cenc.encode(getattr(cenc, name), bad)


def test_sized_uint_decode_truncated_raises():
    from compact_encoding.codec import OutOfBounds

    with pytest.raises(OutOfBounds):
        cenc.decode(cenc.uint24, bytes.fromhex("0102"))  # 2 of 3 bytes
