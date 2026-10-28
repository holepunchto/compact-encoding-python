class State:
    """The ``buffer`` that codecs read and write between ``start`` and ``end``.

    To encode, codecs first advance ``end`` by the size of each value, then
    ``allocate()`` creates the buffer, and codecs write from ``start``. To
    decode, pass the data and codecs read from ``start``.
    """

    def __init__(self, data=None):
        self.start = 0
        if data is None:
            self.end = 0
            self.buffer = bytearray()
        else:
            self.end = len(data)
            self.buffer = data

    @property
    def remaining(self):
        """The number of bytes between ``start`` and ``end``."""
        return self.end - self.start

    def allocate(self):
        """Create a buffer of ``end`` bytes to encode into."""
        self.buffer = bytearray(self.end)

    def rewind(self):
        """Move ``start`` back to the beginning of the buffer."""
        self.start = 0
