#!/usr/bin/env python3
"""Send images to the USB-C RP2040 GDEY075T7 controller (USB CDC protocol v1)."""
import argparse
import json
import secrets
import struct
import time
import zlib
from pathlib import Path

WIDTH, HEIGHT, FRAME_SIZE = 800, 480, 48000
MODES = {"auto": 0, "full": 1, "partial": 2}
HEADER = struct.Struct("<4sBBBBIIII")


def packet(op, seq, payload=b"", mode=0, magic=b"EPD1"):
    prefix = struct.pack("<4sBBBBIII", magic, 1, op, mode, 0, seq,
                         len(payload), zlib.crc32(payload))
    return prefix + struct.pack("<I", zlib.crc32(prefix)) + payload


class ReplyReader:
    def __init__(self):
        self.buffer = bytearray()

    def feed(self, data):
        self.buffer.extend(data)
        replies = []
        while len(self.buffer) >= 4:
            start = self.buffer.find(b"EPA1")
            if start < 0:
                self.buffer[:] = self.buffer[-3:]
                break
            del self.buffer[:start]
            if len(self.buffer) < 24:
                break
            magic, version, op, status, reserved, seq, size, crc, hcrc = HEADER.unpack(self.buffer[:24])
            if (zlib.crc32(self.buffer[:20]) != hcrc or size > 1024 or
                    version != 1 or reserved != 0):
                del self.buffer[0]
                continue
            if len(self.buffer) < 24 + size:
                break
            body = bytes(self.buffer[24:24 + size])
            del self.buffer[:24 + size]
            if zlib.crc32(body) != crc:
                continue
            replies.append((seq, op, status, json.loads(body)))
        return replies


class Device:
    def __init__(self, port, timeout=45):
        import serial
        self.serial = serial.Serial(port, 115200, timeout=0.1, write_timeout=10)
        self.timeout = timeout
        self.reader = ReplyReader()

    def close(self):
        self.serial.close()

    def request(self, op, payload=b"", mode=0):
        seq = secrets.randbits(32)
        data = packet(op, seq, payload, mode)
        # Retransmit a lost ACK with the same sequence; device caches the result.
        for attempt in range(2):
            if self.serial.write(data) != len(data):
                raise IOError("Incomplete USB write; reconnect and retry")
            self.serial.flush()
            end = time.monotonic() + self.timeout
            while time.monotonic() < end:
                for reply_seq, reply_op, status, result in self.reader.feed(self.serial.read(4096)):
                    if reply_seq == seq and reply_op == (op | 0x80):
                        if status:
                            raise RuntimeError(f"Device error {status}: {result}")
                        return result
        raise TimeoutError("No valid response from the e-paper controller")


def convert_image(path, fit="contain", dither=False, threshold=128, rotate=0, invert=False):
    from PIL import Image, ImageOps
    with Image.open(path) as source:
        rgba = ImageOps.exif_transpose(source).convert("RGBA")
    white = Image.new("RGBA", rgba.size, "white")
    image = Image.alpha_composite(white, rgba).convert("L")
    if rotate:
        image = image.rotate(rotate, expand=True)
    if fit == "cover":
        image = ImageOps.fit(image, (WIDTH, HEIGHT), Image.Resampling.LANCZOS)
    elif fit == "stretch":
        image = image.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
    else:
        fitted = ImageOps.contain(image, (WIDTH, HEIGHT), Image.Resampling.LANCZOS)
        image = Image.new("L", (WIDTH, HEIGHT), 255)
        image.paste(fitted, ((WIDTH - fitted.width)//2, (HEIGHT - fitted.height)//2))
    if invert:
        image = ImageOps.invert(image)
    image = image.convert("1", dither=Image.Dither.FLOYDSTEINBERG) if dither else image.point(
        lambda p: 255 if p >= threshold else 0, mode="1")
    data = image.tobytes()  # Row-major, MSB first, 1=white, no row padding at 800px.
    assert len(data) == FRAME_SIZE
    return image, data


def choose_port():
    from serial.tools import list_ports
    ports = [p.device for p in list_ports.comports() if p.vid == 0x2E8A and p.pid == 0xF00A]
    if len(ports) != 1:
        raise RuntimeError("Specify --port /dev/ttyACM0 (or COMn); cannot select one RP2040 CDC device")
    return ports[0]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--port", help="Serial device; otherwise detect one RP2040 USB CDC device")
    sub = ap.add_subparsers(dest="command", required=True)
    sub.add_parser("info")
    sub.add_parser("sleep")
    send = sub.add_parser("send")
    send.add_argument("image", type=Path)
    send.add_argument("--mode", choices=MODES, default="auto")
    send.add_argument("--fit", choices=["contain", "cover", "stretch"], default="contain")
    send.add_argument("--dither", action="store_true", help="Use for photos; threshold is better for text")
    send.add_argument("--threshold", type=int, choices=range(256), default=128, metavar="0..255")
    send.add_argument("--rotate", type=int, choices=[0, 90, 180, 270], default=0)
    send.add_argument("--invert", action="store_true")
    send.add_argument("--preview", type=Path, help="Also save the exact monochrome image sent")
    send.add_argument("--offline", action="store_true", help="Convert/preview without connecting to USB")
    args = ap.parse_args()
    data = b""
    if args.command == "send":
        image, data = convert_image(args.image, args.fit, args.dither, args.threshold, args.rotate, args.invert)
        if args.preview:
            image.save(args.preview)
        if args.offline:
            if not args.preview:
                ap.error("--offline requires --preview")
            print(f"Saved {args.preview}; {len(data)} bytes, CRC32 {zlib.crc32(data):08x}")
            return
    device = Device(args.port or choose_port())
    try:
        info = device.request(1)
        if (info.get("device") != "usb-epaper-reva" or info.get("panel") != "GDEY075T7" or
                info.get("width") != WIDTH or info.get("height") != HEIGHT):
            raise RuntimeError(f"Unexpected controller: {info}")
        result = info if args.command == "info" else device.request(
            3 if args.command == "sleep" else 2, data,
            0 if args.command == "sleep" else MODES[args.mode])
        print(json.dumps(result, indent=2))
    finally:
        device.close()


if __name__ == "__main__":
    main()
