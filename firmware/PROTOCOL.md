# USB CDC binary protocol v1

Stop-and-wait request/response. All multibyte integers are unsigned little-endian. CRC is reflected IEEE CRC32 (polynomial `0xedb88320`, initial/final XOR `0xffffffff`), compatible with `zlib.crc32`. Header length is 24 bytes.

| Offset | Size | Request | Response |
|---:|---:|---|---|
| 0 | 4 | ASCII `EPD1` | ASCII `EPA1` |
| 4 | 1 | Version 1 | Version 1 |
| 5 | 1 | Opcode | Request opcode OR `0x80` |
| 6 | 1 | Mode | Status |
| 7 | 1 | Reserved, must be zero | Zero |
| 8 | 4 | Sequence ID | Same sequence ID |
| 12 | 4 | Payload length | JSON payload length |
| 16 | 4 | Payload CRC32 | JSON payload CRC32 |
| 20 | 4 | CRC32 of first 20 header bytes | Same header check |

Commands: `1=INFO` and `3=SLEEP` have zero payload length, zero payload CRC and mode 0. `2=IMAGE` has exactly **48,000 bytes**, no image file header: 480 rows × 100 bytes, left-to-right, top-to-bottom, most significant bit first, **1=white / 0=black**. Request mode `0=auto`, `1=force full`, `2=prefer partial`; safety baseline and five-partial cleanup apply to both auto and partial modes.

Responses use UTF-8 JSON (under 384 bytes). Status `0=OK`, `1=bad command/version/length/mode`, `2=payload CRC mismatch`, `3=8-second inter-byte timeout`, `4=panel BUSY fault`. Header CRC failures are silently discarded while searching for the next request magic. A timeout before a valid header has no reliable sequence ID: clients should discard unmatching replies. Corrupt or truncated transfers never update the framebuffer baseline.

Always wait for the response before sending another command. Use random sequence IDs across client sessions. The MCU caches its most recent successfully parsed command's ID/opcode/mode/length/CRC and response, including panel faults. Retrying that exact command returns the same result without another refresh. A new sequence ID is necessary to retry after a panel fault. There is no authentication or encryption; access is the physical USB serial interface.
