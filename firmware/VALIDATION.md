# Firmware v1.0.0 validation

Validated 22 November 2026. **Compiled and software-tested; physical board testing remains pending.**

| Check | Result |
|---|---|
| Arduino-Pico 6.4.0 cross-compilation | PASS — Generic RP2040, 125 MHz, 2 MB flash, USB CDC |
| UF2 flash image | Generated; family/address/block audit and SHA256 recorded |
| Program / static RAM | 64,800 / 105,884 bytes |
| Native protocol / refresh policy | PASS under AddressSanitizer and UndefinedBehaviorSanitizer |
| Actual sketch with simulated hardware | PASS — power, baseline, changed region, cleanup, sleep, BUSY fault, retry |
| Python host tests | PASS — four tests; fragmented/corrupt replies and exact pixel packing |
| Offline example conversion | PASS — 48,000 bytes; preview CRC32 `3b9c1544` |
| Panel driver source | Exact GxEPD2 commit and patched-file hashes in `vendor-lock.json` |
| Physical USB enumeration / e-paper waveform / power rails | Not tested |

Tests do not replace electrical bring-up. The UF2 has not been flashed to a physical Rev A board. Use `README.md` for installation and the expected partial/full refresh policy.
