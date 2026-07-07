# compact-encoding-python

Pure-Python port of [compact-encoding](https://github.com/compact-encoding/compact-encoding), wire-compatible with the JavaScript implementation. All multi-byte values are little-endian.

## Usage

```python
import compact_encoding as cenc

data = cenc.encode(cenc.uint, 42)     # -> bytes
n = cenc.decode(cenc.uint, data)      # -> 42
```
