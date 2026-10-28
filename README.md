# compact-encoding-python

Compact encoding schemes for Python. The Python counterpart of [compact-encoding](https://github.com/holepunchto/compact-encoding), and wire compatible with it. All multi-byte values are little-endian.

```
pip install compact-encoding
```

Only the codecs needed by [hyperschema-python](https://github.com/holepunchto/hyperschema-python) and [bare-rpc-python](https://github.com/holepunchto/bare-rpc-python) are included so far. Others, such as `raw`, `any`, `bigint`, and the IP codecs, can be added without changing the wire format.

## Usage

```python
import compact_encoding as cenc

data = cenc.encode(cenc.uint, 42)  # -> bytes
n = cenc.decode(cenc.uint, data)  # -> 42
```

## Codecs

Every codec exposes `preencode`, `encode`, and `decode`. Pass one to the `encode`/`decode` helpers, or drive it directly through a `State` (see [Three-phase API](#three-phase-api)).

### Scalars

| Codec                   | Python type | Notes                      |
| ----------------------- | ----------- | -------------------------- |
| `uint`                  | `int`       | varint, `0 .. 2**53 - 1`   |
| `int`                   | `int`       | zigzag varint              |
| `bool`                  | `bool`      | single byte                |
| `buffer`                | `bytes`     | length-prefixed            |
| `utf8` (alias `string`) | `str`       | length-prefixed UTF-8      |
| `json`                  | any         | length-prefixed UTF-8 JSON |

### Fixed-width numbers

Little-endian, fixed size. Unsigned: `uint8`, `uint16`, `uint24`, `uint32`, `uint40`, `uint48`, `uint56`. Signed: `int24`, `int40`, `int48`, `int56`. IEEE 754 floats: `float32`, `float64`.

### Fixed-width buffers

`fixed(n)` encodes exactly `n` bytes (no length prefix). `fixed32` and `fixed64` are `fixed(32)` and `fixed(64)` - 32- and 64-**byte** buffers, not bits.

### Composites

- `array(codec)` - a length-prefixed list of `codec` values (decode rejects lengths above `0x100000`).
- `record(key_codec, value_codec)` - a length-prefixed dict.
- `frame(codec)` - a nested value with its encoded byte length written ahead of it.

## Encode / decode

`encode(codec, value) -> bytes` and `decode(codec, data) -> value` are the one-shot helpers.

## Three-phase API

To pack several values into one buffer, drive a `State` directly: preencode every value to measure the buffer, `allocate()`, then encode.

```python
import compact_encoding as cenc

state = cenc.State()
cenc.uint.preencode(state, 42)
cenc.utf8.preencode(state, "hi")
state.allocate()
cenc.uint.encode(state, 42)
cenc.utf8.encode(state, "hi")

state = cenc.State(state.buffer)
cenc.uint.decode(state)  # -> 42
cenc.utf8.decode(state)  # -> "hi"
```

A `State` holds `start`, `end`, `buffer`, and a `remaining` property, plus `allocate()` and `rewind()`. `Codec` is a typing `Protocol` for writing your own.

## Errors

`CompactError` is the base error; `OutOfBounds` (a subclass) is raised when a decode reads past the end of the buffer. Out-of-range encodes raise `ValueError`.

## License

Apache-2.0
