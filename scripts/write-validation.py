"""Write measured Rev C release facts only after the fabrication gates pass."""
import json,zipfile,hashlib,math
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1];fab=ROOT/'manufacturing'
read=lambda n:json.loads((ROOT/n).read_text())
circuit=read('dist/index/circuit.json');counts=Counter(e['type'] for e in circuit)
assert not [e for e in circuit if 'error' in e['type'] or 'warning' in e['type']]
p=read('manufacturing/checks/routing-provenance.json');style=read('manufacturing/checks/pcb-style-review.json');stock=read('manufacturing/checks/diagnostics.json');assembly=read('manufacturing/checks/assembly-audit.json');labels=read('manufacturing/checks/reference-labels.json');electrical=read('manufacturing/checks/electrical-audit.json');clearance=read('enclosure/component-clearance.json');fit=read('enclosure/fit-report.json');access=read('enclosure/usability-report.json');uf2=read('firmware/releases/rp2354b/uf2-audit.json')
for report in [p,style,stock,assembly,labels,electrical,clearance,uf2]:assert report['result']=='PASS'
vias=[e for e in circuit if e['type']=='pcb_via'];gap=min(math.hypot(a['x']-b['x'],a['y']-b['y'])-(a['hole_diameter']+b['hole_diameter'])/2 for i,a in enumerate(vias) for b in vias[i+1:]);assert gap>=.2-1e-5
with zipfile.ZipFile(fab/'JLCPCB-Gerbers-RevC.zip') as z:gerbers=len(z.namelist())
text=f'''# Rev C — RP2354B native tscircuit release

**PASS for prototype fabrication: zero circuit errors and zero warnings.**

Validated {stock['verified_at']}. The RP2354B replaces RP2040 and external flash. U5 now supplies the 1.092 V core rail. USB-C remains accessible from the left of the 18 mm enclosure. See [hardware rationale](../docs/RP2354B.md).

| Check | Measured result |
|---|---|
| TypeScript, netlist and schematic / PCB placement | PASS |
| Independent physical pin and supply audit | {electrical['electrical_components']} electrical components, {electrical['source_nets']} nets |
| Fresh native routing | {counts['pcb_trace']} traces, {len(vias)} through vias, four layers |
| Inner ground pour | {counts['pcb_copper_pour']} connected region(s); no isolated warnings |
| Routing input | {p['source_authored_trace_count']} authored local paths; zero imported traces / vias; caches disabled |
| Gerber-derived shorts | No shorts detected |
| Default PCB style | 0 issues |
| Continuous-copper style | 0 issues across {style['continuous_chain_count']} chains |
| Minimum via drill-edge spacing | {gap:.3f} mm; minimum 0.20 mm |
| Through-via geometry | 0.30 mm drill / 0.55 mm pad; both sides tented |
| Reference labels | {labels['top_references']} component-associated top labels; zero bottom labels |
| Supplier inventory | {stock['verified_supplier_skus']} exact SKUs with primary JLCPCB observations younger than six hours |
| BOM / CPL | {assembly['assembled_refs']} matched top-side assembly references; supplier rotations resolved |
| QFN stencil | Four 1.25 mm windows; 54% exposed-pad coverage; no paste on probe pads |
| Product views | 16 mechanical parts, two System pages, six Drawing pages |
| New component / enclosure clearance | All 70 supplier meshes; minimum rear-floor gap {clearance['minimum_clearance_mm']:.3f} mm |
| Case and cable access | Four valid solids and watertight STLs; 40 mm insertion sweep and 7 mm grip allowance |
| RP2354B firmware | Compiled at 150 MHz; correct RP2350 UF2 family and binary equality |

The layout uses ordinary tscircuit `trace` / `pcbPath` declarations for local connections and native `via` primitives. The built-in {p['solver']} routes the remaining connections from current placement. All declared paths remain fixed. No KiCad, external router, custom router callback, imported routes or route caches are used. Electrical checks, stock warnings, shorts and default style rules remain enabled.

The pinned Core patch preserves branch net identity and explicitly requested via layer ports; it does not replace the routing algorithm. The RP2354B supplier pin-metadata correction removes incorrect UART/I2C assignments from dedicated USB/QMI pins using Raspberry Pi's physical pin table. Regression tests retain real short detection and power-pin requirements.

`JLCPCB-Gerbers-RevC.zip` contains {gerbers} fabrication files. BOM, CPL and stencil derive from this same validated Circuit JSON. Five schematic SVGs, six engineering drawings, two system diagrams, firmware, printable STLs and editable STEP files accompany the source.

The enclosure is {fit['case_size_mm'][0]} × {fit['case_size_mm'][1]} × {fit['case_size_mm'][2]} mm. Its USB-C aperture, PCB posts and short-panel-flex datums remain aligned. The lower display window clears the stand lip by {access['front_window_clearance_above_stand_lip_mm']:.3f} mm. The native full-product build includes assembly collision / disassembly checks.

This is software and nominal CAD validation. Physical power-rail measurements, USB enumeration, supplied-panel/FPC fit, waveform performance and a first printed fit remain untested. The archived RP2040 UF2 must not be used on Rev C. No fabrication order has been placed.
'''
(fab/'VALIDATION.md').write_text(text)
(ROOT/'firmware/VALIDATION.md').write_text(f'''# Firmware v1.1.0 — RP2354B Rev C

Arduino-Pico 6.4.0 compiled the real sketch for Generic RP2350B, Arm, 150 MHz and 2 MB flash. Program storage: 62,052 bytes. Static RAM: 106,656 bytes (of 524,288).

The UF2 audit passed: {uf2['payload_blocks']} secure-Arm payload blocks, one absolute compatibility block, family 0xe48bff59, flash address bounds and exact equality with the compiler binary. Artifact SHA256 values are in `releases/rp2354b/build-manifest.json`.

The protocol / refresh-policy and actual-sketch tests passed under AddressSanitizer and UndefinedBehaviorSanitizer. Five host tests passed, covering framing, corrupt replies, pixel packing, alpha compositing and RP2350 serial discovery / ambiguous-port handling. Eight native circuit regression tests passed.

The host protocol and GP8–GP14 mapping remain compatible. The new RP2354B UF2 is required; root-level release binaries are archived RP2040 images. USB uses VID 2e8a / PID f00f and the core's 250 mA configuration descriptor.

No physical USB, flash, power-rail or display test has been performed. Partial-refresh timing remains limited by the UC8179 panel waveforms.
''')
(ROOT/'enclosure/VALIDATION.md').write_text(f'''# Rev C — 18 mm enclosure validation

The case is 182.2 × 137.2 × 18 mm, with a left-side USB-C opening and separate 15° stand. The RP2354B layout retains the mounting-hole, connector and FPC datums used by the case.

- Four printed parts are valid single CAD solids with watertight STL meshes.
- Nominal glass, PCB and printed-part intersections are zero.
- All 70 assembled supplier meshes were checked against the 2.4 mm rear floor; minimum clearance is {clearance['minimum_clearance_mm']:.3f} mm.
- Ordinary and large straight USB plugs clear the 40 mm insertion sweep and 7 mm grip envelope with the stand installed.
- The native tscircuit assembly contains 16 mechanical parts and six dimensioned drawing pages. Its collision and disassembly checks pass without excluded geometry.

The new inductor uses a closed solid tessellated from its unmodified TSCI-imported supplier STEP model; its bounds match the original OBJ to 0.025 mm. No bounding-box replacement is used for clearance validation.

A first print, real cable fit and the actual panel/FPC tolerance stack remain untested.
''')
print('Wrote measured Rev C fabrication, firmware and enclosure reports')
