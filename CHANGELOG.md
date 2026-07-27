# Changelog

## 1.0.0

First stable release.

- Binary wire codec, wire-compatible with the JavaScript `compact-encoding` reference (byte-exact vectors in the test suite).
- Codecs: `uint`, `int`, `bool`, `buffer`, `utf8`/`string`, `json`; the sized integers `uint8`-`uint56` and `int24`-`int56`; `float32`/`float64`; `fixed(n)`/`fixed32`/`fixed64`; and the composites `array`, `record`, `frame`.
- One-shot `encode`/`decode` helpers plus the three-phase `State` API.
- Zero runtime dependencies.
