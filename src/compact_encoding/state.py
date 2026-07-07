class State:
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
        return self.end - self.start

    def allocate(self):
        self.buffer = bytearray(self.end)

    def rewind(self):
        self.start = 0
