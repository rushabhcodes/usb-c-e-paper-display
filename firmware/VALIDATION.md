# Firmware v1.1.0 — RP2354B Rev C

Arduino-Pico 6.4.0 compiled the real sketch for Generic RP2350B, Arm, 150 MHz and 2 MB flash. Program storage: 62,052 bytes. Static RAM: 106,656 bytes (of 524,288).

The UF2 audit passed: 315 secure-Arm payload blocks, one absolute compatibility block, family 0xe48bff59, flash address bounds and exact equality with the compiler binary. Artifact SHA256 values are in `releases/rp2354b/build-manifest.json`.

The protocol / refresh-policy and actual-sketch tests passed under AddressSanitizer and UndefinedBehaviorSanitizer. Five host tests passed, covering framing, corrupt replies, pixel packing, alpha compositing and RP2350 serial discovery / ambiguous-port handling. Eight native circuit regression tests passed.

The host protocol and GP8–GP14 mapping remain compatible. The new RP2354B UF2 is required; root-level release binaries are archived RP2040 images. USB uses VID 2e8a / PID f00f and the core's 250 mA configuration descriptor.

No physical USB, flash, power-rail or display test has been performed. Partial-refresh timing remains limited by the UC8179 panel waveforms.
