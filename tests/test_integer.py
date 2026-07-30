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


def test_uint_decode_beyond_max_safe_integer_raises():
    # A full 8-byte varint payload holds far more than a JS Number, where the
    # reference raises from validateSafeUint. Python ints would return it.
    with pytest.raises(ValueError):
        cenc.decode(cenc.uint, b"\xff" * 9)  # FF marker + 8 bytes of 0xff


def test_uint_decode_max_safe_integer_is_allowed():
    # The guard is off-by-none: the ceiling itself must still decode.
    assert cenc.decode(cenc.uint, bytes.fromhex("ffffffffffffff1f00")) == MAX_SAFE


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


def test_uint56_decode_beyond_max_safe_integer_raises():
    with pytest.raises(ValueError):
        cenc.decode(cenc.uint56, b"\xff" * 7)  # 2**56 - 1


@pytest.mark.parametrize(
    "name,nbytes,widest",
    [
        ("uint8", 1, 2**8 - 1),
        ("uint16", 2, 2**16 - 1),
        ("uint24", 3, 2**24 - 1),
        ("uint40", 5, 2**40 - 1),
        ("uint48", 6, 2**48 - 1),
    ],
)
def test_narrow_sized_uint_decode_cannot_overflow(name, nbytes, widest):
    # JS guards only uint56 and uint64 on decode because nothing narrower can
    # exceed MAX_SAFE_INTEGER. Pin that reasoning so the guard is not "tidied"
    # into the narrow codecs, or removed from the wide ones.
    assert widest <= MAX_SAFE
    assert cenc.decode(getattr(cenc, name), b"\xff" * nbytes) == widest


SIZED_INT_CASES = [
    ("int24", 0, "000000"),
    ("int24", -1, "010000"),
    ("int24", 1, "020000"),
    ("int24", 8388607, "feffff"),  # 2**23 - 1
    ("int24", -8388608, "ffffff"),  # -2**23
    ("int40", -1, "0100000000"),
    ("int40", 549755813887, "feffffffff"),  # 2**39 - 1
    ("int40", -549755813888, "ffffffffff"),  # -2**39
    ("int48", -1, "010000000000"),
    ("int48", 140737488355327, "feffffffffff"),  # 2**47 - 1
    ("int48", -140737488355328, "ffffffffffff"),  # -2**47
    ("int56", -1, "01000000000000"),
    ("int56", 4503599627370495, "feffffffffff1f"),  # 2**52 - 1 (fixture 42)
    ("int56", -4503599627370496, "ffffffffffff1f"),  # -2**52 (fixture 42)
]


@pytest.mark.parametrize("name,value,hexbytes", SIZED_INT_CASES)
def test_sized_int_encode(name, value, hexbytes):
    assert cenc.encode(getattr(cenc, name), value).hex() == hexbytes


@pytest.mark.parametrize("name,value,hexbytes", SIZED_INT_CASES)
def test_sized_int_decode(name, value, hexbytes):
    assert cenc.decode(getattr(cenc, name), bytes.fromhex(hexbytes)) == value


@pytest.mark.parametrize(
    "name,bad",
    [
        ("int24", 8388608),  # 2**23; zigzag -> 2**24, overflows uint24
        ("int24", -8388609),  # -(2**23) - 1; zigzag overflows uint24
        ("int56", 2**52),  # zigzag -> 2**53 > MAX_SAFE
        ("int56", -(2**52) - 1),
    ],
)
def test_sized_int_rejects_out_of_range(name, bad):
    with pytest.raises(ValueError):
        cenc.encode(getattr(cenc, name), bad)


def test_sized_int_decode_truncated_raises():
    from compact_encoding.codec import OutOfBounds

    with pytest.raises(OutOfBounds):
        cenc.decode(cenc.int40, bytes.fromhex("010203"))  # 3 of 5 bytes


def test_sized_int_decode_beyond_max_safe_integer_raises():
    # int56 wraps uint56, so it inherits the decode guard - matching JS, where
    # int56 is zigZagInt(uint56) and the guard lives in uint56.decode.
    with pytest.raises(ValueError):
        cenc.decode(cenc.int56, b"\xff" * 7)
