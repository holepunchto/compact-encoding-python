from compact_encoding.state import State


def test_empty_state():
    s = State()
    assert s.start == 0
    assert s.end == 0
    assert s.buffer == bytearray()
    assert s.remaining == 0


def test_state_from_data():
    s = State(b"\x01\x02\x03")
    assert s.start == 0
    assert s.end == 3
    assert s.buffer == b"\x01\x02\x03"
    assert s.remaining == 3


def test_allocate_sizes_buffer_to_end():
    s = State()
    s.end = 4
    s.allocate()
    assert s.buffer == bytearray(4)
    assert s.start == 0


def test_rewind_resets_start():
    s = State(b"\x01\x02")
    s.start = 2
    s.rewind()
    assert s.start == 0
