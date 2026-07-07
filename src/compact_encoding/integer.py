from .codec import OutOfBounds

MAX_SAFE_INTEGER = 2**53 - 1


def _validate_uint(n):
    if not (n >= 0):
        raise ValueError("uint must be positive")
    if n > MAX_SAFE_INTEGER:
        raise ValueError(
            "integer is greater than the maximum safe integer, use biguint/bigint"
        )


def _read_le(state, n):
    if state.remaining < n:
        raise OutOfBounds("Out of bounds")
    s = state.start
    value = int.from_bytes(state.buffer[s : s + n], "little")
    state.start = s + n
    return value


class _UInt:
    def preencode(self, state, n):
        _validate_uint(n)
        if n <= 0xFC:
            state.end += 1
        elif n <= 0xFFFF:
            state.end += 3
        elif n <= 0xFFFFFFFF:
            state.end += 5
        else:
            state.end += 9

    def encode(self, state, n):
        _validate_uint(n)
        s = state.start
        if n <= 0xFC:
            state.buffer[s] = n
            state.start = s + 1
        elif n <= 0xFFFF:
            state.buffer[s] = 0xFD
            state.buffer[s + 1 : s + 3] = n.to_bytes(2, "little")
            state.start = s + 3
        elif n <= 0xFFFFFFFF:
            state.buffer[s] = 0xFE
            state.buffer[s + 1 : s + 5] = n.to_bytes(4, "little")
            state.start = s + 5
        else:
            state.buffer[s] = 0xFF
            state.buffer[s + 1 : s + 9] = n.to_bytes(8, "little")
            state.start = s + 9

    def decode(self, state):
        a = _read_le(state, 1)
        if a <= 0xFC:
            return a
        if a == 0xFD:
            return _read_le(state, 2)
        if a == 0xFE:
            return _read_le(state, 4)
        return _read_le(state, 8)


def _validate_uint32(n):
    if not (n >= 0):
        raise ValueError("uint32 must be positive")
    if n > 0xFFFFFFFF:
        raise ValueError("uint32 is out of range")


class _UInt32:
    def preencode(self, state, n):
        _validate_uint32(n)
        state.end += 4

    def encode(self, state, n):
        _validate_uint32(n)
        s = state.start
        state.buffer[s : s + 4] = n.to_bytes(4, "little")
        state.start = s + 4

    def decode(self, state):
        return _read_le(state, 4)


def _zigzag(n):
    if n < 0:
        return 2 * -n - 1
    return 2 * n


def _unzigzag(z):
    if z == 0:
        return 0
    if z & 1 == 0:
        return z // 2
    return -(z + 1) // 2


class _Int:
    def preencode(self, state, n):
        uint.preencode(state, _zigzag(n))

    def encode(self, state, n):
        uint.encode(state, _zigzag(n))

    def decode(self, state):
        return _unzigzag(uint.decode(state))


uint = _UInt()
uint32 = _UInt32()
int_codec = _Int()
