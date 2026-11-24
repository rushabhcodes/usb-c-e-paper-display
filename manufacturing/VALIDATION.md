# Rev C — RP2354B native tscircuit release

**PASS for prototype fabrication: zero circuit errors and zero warnings.**

Validated 2026-11-24T18:03:27.382197+00:00. The RP2354B replaces RP2040 and external flash. U5 now supplies the 1.092 V core rail. USB-C remains accessible from the left of the 18 mm enclosure. See [hardware rationale](../docs/RP2354B.md).

| Check | Measured result |
|---|---|
| TypeScript, netlist and schematic / PCB placement | PASS |
| Independent physical pin and supply audit | 76 electrical components, 42 nets |
| Fresh native routing | 202 traces, 132 through vias, four layers |
| Inner ground pour | 1 connected region(s); no isolated warnings |
| Routing input | 119 authored local paths; zero imported traces / vias; caches disabled |
| Gerber-derived shorts | No shorts detected |
| Default PCB style | 0 issues |
| Continuous-copper style | 0 issues across 194 chains |
| Minimum via drill-edge spacing | 0.427 mm; minimum 0.20 mm |
| Through-via geometry | 0.30 mm drill / 0.55 mm pad; both sides tented |
| Reference labels | 76 component-associated top labels; zero bottom labels |
| Supplier inventory | 28 exact SKUs with primary JLCPCB observations younger than six hours |
| BOM / CPL | 70 matched top-side assembly references; supplier rotations resolved |
| QFN stencil | Four 1.25 mm windows; 54% exposed-pad coverage; no paste on probe pads |
| Product views | 16 mechanical parts, two System pages, six Drawing pages |
| New component / enclosure clearance | All 70 supplier meshes; minimum rear-floor gap 2.099 mm |
| Case and cable access | Four valid solids and watertight STLs; 40 mm insertion sweep and 7 mm grip allowance |
| RP2354B firmware | Compiled at 150 MHz; correct RP2350 UF2 family and binary equality |

The layout uses ordinary tscircuit `trace` / `pcbPath` declarations for local connections and native `via` primitives. The built-in AutoroutingPipelineSolver9_PreloadedTraceGraph routes the remaining connections from current placement. All declared paths remain fixed. No KiCad, external router, custom router callback, imported routes or route caches are used. Electrical checks, stock warnings, shorts and default style rules remain enabled.

The pinned Core patch preserves branch net identity and explicitly requested via layer ports; it does not replace the routing algorithm. The RP2354B supplier pin-metadata correction removes incorrect UART/I2C assignments from dedicated USB/QMI pins using Raspberry Pi's physical pin table. Regression tests retain real short detection and power-pin requirements.

`JLCPCB-Gerbers-RevC.zip` contains 13 fabrication files. BOM, CPL and stencil derive from this same validated Circuit JSON. Five schematic SVGs, six engineering drawings, two system diagrams, firmware, printable STLs and editable STEP files accompany the source.

The enclosure is 182.2 × 137.2 × 18.0 mm. Its USB-C aperture, PCB posts and short-panel-flex datums remain aligned. The lower display window clears the stand lip by 5.275 mm. The native full-product build includes assembly collision / disassembly checks.

This is software and nominal CAD validation. Physical power-rail measurements, USB enumeration, supplied-panel/FPC fit, waveform performance and a first printed fit remain untested. The archived RP2040 UF2 must not be used on Rev C. No fabrication order has been placed.
