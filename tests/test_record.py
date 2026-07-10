import pytest

import compact_encoding as cenc

# record(string, uint): uint(count) + (key, value) pairs in insertion order.
# Vectors from hyperschema-test fixture 23.
RECORD_CASES = [
    ({}, "00"),
    ({"x": 0}, "01017800"),
    ({"alice": 10, "bob": 20}, "0205616c6963650a03626f6214"),
]


@pytest.mark.parametrize("value,hexbytes", RECORD_CASES)
def test_record_encode(value, hexbytes):
    assert cenc.encode(cenc.record(cenc.string, cenc.uint), value).hex() == hexbytes


@pytest.mark.parametrize("value,hexbytes", RECORD_CASES)
def test_record_decode(value, hexbytes):
    assert (
        cenc.decode(cenc.record(cenc.string, cenc.uint), bytes.fromhex(hexbytes))
        == value
    )


def test_record_preserves_insertion_order_not_sorted():
    # {"b": 2, "a": 1} must encode b before a (insertion order), NOT sorted.
    # count 02 + "b"(0162)+uint2(02) + "a"(0161)+uint1(01)
    codec = cenc.record(cenc.string, cenc.uint)
    assert cenc.encode(codec, {"b": 2, "a": 1}).hex() == "02016202016101"
    assert cenc.decode(codec, bytes.fromhex("02016202016101")) == {"b": 2, "a": 1}
