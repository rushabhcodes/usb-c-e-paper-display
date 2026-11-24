# USB image firmware — PCB Rev C / RP2354B

The ready-to-flash image is `releases/rp2354b/USB-Epaper-RevC-RP2354B-v1.1.0.uf2`. It targets this project's bare RP2354B, 12 MHz crystal, 2 MB internal flash and **raw Good Display GDEY075T7 / UC8179**. It does not target the earlier Waveshare 3.97-inch display or a generic e-paper HAT.

## Install and send an image

1. Connect the panel to J2 with USB disconnected. Confirm contact orientation and close the ZIF latch.
2. Connect USB-C with a data cable. Hold **BOOTSEL / SW1**, press and release **RESET / SW2**, then release BOOTSEL.
3. Copy `USB-Epaper-RevC-RP2354B-v1.1.0.uf2` to the **RP2350** USB drive. The board restarts as USB CDC serial (VID `2e8a`, PID `f00f`).
4. Install the host dependencies and upload:

```sh
python -m venv .venv-host
. .venv-host/bin/activate
python -m pip install -r firmware/host/requirements.txt
python firmware/host/epaper.py --port /dev/ttyACM0 info
python firmware/host/epaper.py --port /dev/ttyACM0 send firmware/examples/dashboard-41.png
python firmware/host/epaper.py --port /dev/ttyACM0 send firmware/examples/dashboard-42.png
```

Use `COM5` on Windows or `/dev/cu.usbmodem…` on macOS. `--port` may be omitted when exactly one matching RP2040/RP2350 device is connected. Linux serial access depends on your local device permissions; close other serial monitors before using the sender.

RP2354B runs at 150 MHz with 520 KB RAM. The compiler reports 62,052 bytes of program storage and 106,656 bytes of global RAM for this build. Archived files directly under `releases/` target the older RP2040 board.

The first image gets a full refresh; the second example changes only the minute and progress bar and gets a fast partial update. USB-C carries this application protocol, rather than USB video or DisplayPort. A full 48,000-byte monochrome image is transferred each time; the MCU computes the changed rectangle.

```sh
# Photos: grayscale conversion, Floyd–Steinberg dithering, letterboxed to 800 x 480
python firmware/host/epaper.py --port /dev/ttyACM0 send photo.jpg --dither --preview converted.png
# Text/line art: threshold conversion is the default
python firmware/host/epaper.py --port /dev/ttyACM0 send dashboard.png --mode partial
# Force a clean full refresh, even if pixels are unchanged
python firmware/host/epaper.py --port /dev/ttyACM0 send dashboard.png --mode full
# Deep sleep, regulator off; the next image automatically restores a full baseline
python firmware/host/epaper.py --port /dev/ttyACM0 sleep
# Convert without a board
python firmware/host/epaper.py send photo.jpg --dither --offline --preview converted.png
```

`--fit contain` preserves aspect ratio with white margins; `cover` crops; `stretch` fills. `--rotate 90`, `--invert` and `--threshold 0..255` are also available. Transparent images are composited over white. There is no persistent image storage or automatic slideshow: the panel retains its visible image when USB is removed, and a computer sends subsequent updates.

## Refresh and power behavior

- GP14 remains low at boot, INFO and failed/incomplete transfers. SPI/control inputs are low while the panel regulator is off.
- SPI1 uses SCK **GP10**, MOSI **GP11**, software CS **GP9**, DC **GP8**, RESET **GP12**, BUSY **GP13 active low**, enable **GP14**. MISO is explicitly disabled so SPI cannot take GP12 away from RESET. SPI runs at 4 MHz.
- Two 48,000-byte framebuffers hold the last successful image and the incoming candidate. Header and payload CRC32 must pass before touching the panel.
- The first image after boot, sleep or a fault uses the normal full waveform and explicitly seeds previous-image RAM. The library's accelerated full waveform is disabled for periodic ghost clearing.
- Subsequent changed images use the vendor-derived fast differential OTP waveform. Only the byte-aligned changed rectangle is written over SPI. GxEPD2's `usePartialUpdateWindow=false` is retained for image quality: the differential waveform drives the full panel; unchanged pixels are retained.
- After **five successful partial updates**, the next changed image gets a full refresh. Identical images in auto/partial mode perform no refresh. `--mode partial` preserves the baseline and cleanup rules.
- The boost/high-voltage generator is turned off after each refresh. Logic power stays on to retain the controller's previous-image RAM. `sleep` completes hibernation, takes control signals low, then removes display power and invalidates the baseline.
- A BUSY wait exceeding 10 seconds raises a sticky fault, cuts panel power and invalidates the baseline. Send a new request after checking hardware to recover. An incomplete upload times out after 8 seconds without changing the display.

The manufacturer lists approximately **0.3 s partial / 3 s full at 25 °C**. The upstream driver gives a measured partial BUSY time near 0.45 s; USB, RAM writes and power sequences add time. Response JSON reports actual `elapsed_ms`, chosen `mode`, byte-aligned `bbox`, and partial count. Fast refresh performance, ghosting, supply voltages and temperature behavior still require testing on a fabricated board. Start at room temperature; use full mode when evaluating temperature extremes. This firmware does not measure ambient temperature or promise video frame rates.

## Build and test

```sh
# Requires arduino-cli on PATH; isolated downloads do not modify global Arduino packages
python firmware/build.py --install
# Rebuild with the already installed toolchain
python firmware/build.py
# Requires g++, Python, Pillow; uses ASan + UBSan, no connected hardware
python firmware/test.py
```

Pinned Arduino-Pico **6.4.0**, Generic RP2350 with **RP2350B** variant, Arm Cortex-M33, **150 MHz**, 2 MB internal flash/no filesystem, Pico SDK USB CDC and size optimization. The build uses **62,052 bytes program storage / 106,656 bytes static RAM** (20%). `releases/rp2354b/build-manifest.json` records the complete FQBN and SHA256 hashes. The UF2 auditor checks the RP2350 secure-Arm family and the ROM compatibility block, then compares the flash payload against the compiled binary.

The tests cover CRC vectors, corrupt headers and payloads, resynchronization, bounded payload sizes, fragmented replies, timeouts, image packing, transparency, byte-aligned differences, first-frame baseline, cleanup cadence, no-op images, sleep, power sequencing, BUSY faults and retry replay. The application tests compile the actual sketch against fake hardware boundaries. They do not establish physical USB enumeration or waveform performance.

## Sources and license

The small GxEPD2 driver subset is included locally, preserving upstream notices and GPL v3 text. `vendor-lock.json` records the exact upstream commit and local file hashes. Changes: relative includes, a sticky BUSY-timeout flag in place of serial diagnostic output, and normal full-refresh selection. The fast partial LUT/OTP sequence is unchanged. Application and host code are provided under GPL-3.0; see `COPYING`. Arduino-Pico includes separately licensed dependencies; its release sources and notices are available upstream.

- [GDEY075T7 specifications](https://www.good-display.com/product/396.html)
- [Pinned GxEPD2 source](https://github.com/ZinggJM/GxEPD2/tree/de82887e77a78528ea386e68bba2cb0291d2c319)
- [Arduino-Pico 6.4.0](https://github.com/earlephilhower/arduino-pico/releases/tag/6.4.0)
- [SPI pin selection and NOPIN](https://arduino-pico.readthedocs.io/en/latest/spi.html)
