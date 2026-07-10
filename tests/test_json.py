import pytest

import compact_encoding as cenc

# value -> exact hex of <uint length byte(s)><utf8 of the JSON text>.
# Cross-checked against JS compact-encoding and hyperschema-test fixture 25.
JSON_CASES = [
    ({"key": "value"}, "0f7b226b6579223a2276616c7565227d"),
    ({}, "027b7d"),
    ([], "025b5d"),
    ([1, 2, 3], "075b312c322c335d"),
    ("just a string", "0f226a757374206120737472696e6722"),
    (42, "023432"),
    (True, "0474727565"),
    (None, "046e756c6c"),
    (
        {"nested": {"deep": [1, "two", False]}},
        "237b226e6573746564223a7b2264656570223a5b312c2274776f222c66616c73655d7d7d",
    ),
]


@pytest.mark.parametrize("value,hexbytes", JSON_CASES)
def test_json_encode(value, hexbytes):
    assert cenc.encode(cenc.json, value).hex() == hexbytes


@pytest.mark.parametrize("value,hexbytes", JSON_CASES)
def test_json_decode(value, hexbytes):
    assert cenc.decode(cenc.json, bytes.fromhex(hexbytes)) == value


def test_json_no_spaces_and_raw_unicode():
    # JS JSON.stringify emits no spaces and raw UTF-8 (not \\uXXXX).
    assert cenc.encode(cenc.json, {"a": 1, "b": 2})[1:].decode() == '{"a":1,"b":2}'
    assert cenc.encode(cenc.json, "smrtør")[1:].decode() == '"smrtør"'


def test_json_decode_truncated_raises():
    from compact_encoding.codec import OutOfBounds

    # length prefix says 15 bytes, only 2 follow
    with pytest.raises(OutOfBounds):
        cenc.decode(cenc.json, bytes.fromhex("0f7b7d"))
