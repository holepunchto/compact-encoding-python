# compact-encoding-python

Pure-Python port of [compact-encoding](https://github.com/compact-encoding/compact-encoding), wire-compatible with the JavaScript implementation. All multi-byte values are little-endian.

## Usage

```python
import compact_encoding as cenc

data = cenc.encode(cenc.uint, 42)     # -> bytes
n = cenc.decode(cenc.uint, data)      # -> 42
```

## Codecs

`uint`, `uint32`, `int`, `utf8` (alias `string`), `bool`, `buffer`.

## Three-phase API

```python
import compact_encoding as cenc

state = cenc.State()
cenc.uint.preencode(state, 42)
cenc.utf8.preencode(state, "hi")
state.allocate()
cenc.uint.encode(state, 42)
cenc.utf8.encode(state, "hi")
```
