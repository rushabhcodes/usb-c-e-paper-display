"""Validate the RP2350 secure-Arm UF2 container against its compiled binary."""
import json
import struct
from pathlib import Path


def audit(release: Path):
    data = (release / 'usb_epaper.ino.uf2').read_bytes()
    assert data and len(data) % 512 == 0
    payload, absolute = {}, []
    for offset in range(0, len(data), 512):
        block = data[offset:offset + 512]
        m0, m1, flags, addr, size, idx, total, family = struct.unpack('<8I', block[:32])
        assert (m0, m1) == (0x0a324655, 0x9e5d5157)
        assert struct.unpack('<I', block[-4:])[0] == 0x0ab16f30
        assert size == 256 and flags & 0x2000
        if family == 0xe48bff57:  # picotool --abs-block ROM compatibility block
            assert flags == 0xa000 and addr == 0x10ffff00 and idx == 0 and total == 2
            absolute.append(block)
        else:
            assert family == 0xe48bff59 and flags == 0x2000
            assert 0x10000000 <= addr and addr + size <= 0x10200000
            assert idx not in payload
            payload[idx] = (addr, total, block[32:32 + size])
    assert len(absolute) == 1 and payload
    assert set(payload) == set(range(len(payload)))
    assert all(addr == 0x10000000 + i * 256 and total == len(payload)
               for i, (addr, total, _) in payload.items())
    binary = (release / 'usb_epaper.ino.bin').read_bytes()
    joined = b''.join(payload[i][2] for i in range(len(payload)))
    assert joined[:len(binary)] == binary and len(joined) - len(binary) < 256
    report = {'result': 'PASS', 'mcu': 'RP2354B',
              'uf2_family': 'RP2350 ARM secure / 0xe48bff59',
              'absolute_family': 'RP2350 / 0xe48bff57',
              'absolute_blocks': len(absolute), 'payload_blocks': len(payload),
              'payload_size': 256, 'flash_base': '0x10000000',
              'flash_capacity_bytes': 2097152, 'uf2_matches_bin': True,
              'physical_board_tested': False}
    (release / 'uf2-audit.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


if __name__ == '__main__':
    print(json.dumps(audit(Path(__file__).parent / 'releases/rp2354b'), indent=2))
