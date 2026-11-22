# Rev A — tscircuit routing release

**PASS for prototype fabrication — zero default PCB-style findings.**

Validated 22 November 2026. This two-layer release fixes the four long angled runs and one staircase reported in the previous native routing. Board dimensions, mounting holes, connectors, component placements and GPIO assignments are unchanged.

| Check | Result |
|---|---|
| TypeScript and tscircuit build | PASS; zero circuit errors |
| Electrical netlist | 0 errors, 0 warnings |
| Schematic placement | PASS; three sheets |
| PCB component placement | 0 errors, 0 warnings |
| Independent device-pin and supply audit | PASS; 68 electrical components, 45 nets |
| Routing provenance | PASS; five TSX-authored inputs, zero imported board routes, caches disabled |
| Routing | 165 trace records, 151 through vias; two copper layers, three bottom ground-pour regions |
| Gerber-derived shorts check | No shorts detected |
| Default PCB style | 0 long odd-angle runs; 0 staircases |
| Continuous-copper style check | PASS; zero findings across 238 chains |
| Drill spacing | Minimum 0.270 mm between via drill edges; required 0.20 mm |
| Via geometry | 0.15 mm drills, 0.30 mm pads; both sides tented by board default |
| USB plated slots | 0.8 × 1.6 mm; 0.20 mm minimum annular ring |
| BOM/CPL | 62 matched references; all supplier codes and orientations resolved |
| Stencil | Four RP2040 exposed-pad windows, about 55% coverage; no paste on probe pads |

All copper is authored and generated with tscircuit. `product/controller-board.tsx` defines RUN, DC, CS, BUSY and display SCK using standard `trace` / `pcbPaths` primitives with straight and 45° segments. Numeric coordinates are anchored to TP6 at the board centre; component selectors supply the endpoints. Explicit wire landings represent continuity at vias. These paths were newly authored in TSX, rather than imported from a previously routed board.

The initial routing input contains exactly those five source-authored paths. The built-in `bus_lanes` phase adds five top-layer crystal paths. The general local tscircuit solver receives those ten paths, refines portions of the five authored signals for clearance, and completes the remaining connections. Both phases report cache disabled. The released build uses tscircuit **0.0.3277**, Core **0.0.2458** and capacity-autorouter **0.0.1153**, pinned by the package and lockfile. No KiCad, external router, custom routing algorithm or saved-board-route import is used.

`checks/routing-provenance.json` identifies the authored inputs and native refinements and records source/config/output hashes. `checks/native-routing/` contains the actual stage inputs, outputs, images and timing; these diagnostics are output artifacts, never routing inputs to the project. `checks/pcb-style.txt`, `checks/continuous-style.txt` and their SVGs record the unmodified default checks. The continuous-copper check joins unbranched same-net edges for verification, so trace-record boundaries cannot hide an angle or staircase. It never changes fabrication geometry.

Routing requests 0.15 mm clearance, with a 0.10 mm final trace-clearance floor matching JLCPCB's published minimum for two-layer, 1 oz boards. Via-to-pad and pad-to-pad clearances remain 0.12 mm. The 0.15 mm drill option carries a surcharge; see `ORDERING.md`.

`JLCPCB-Gerbers-RevA.zip` contains eleven files: two copper layers, masks, legends, paste layers, outline, plated drilling and non-plated drilling. `BOM.csv` and `CPL.csv` are supplied separately. These are exported directly from the validated tscircuit Circuit JSON. The complete package includes the editable design, firmware, enclosure and runtime configuration.

Imported generic chips can produce non-blocking pin-description and supplier-availability warnings. The independent pin audit covers their device connections; inventory is confirmed during the JLCPCB quote.

This is file-level validation. A fabricated prototype still needs power-rail, USB, FPC and refresh testing. Firmware passes compilation and software tests; enclosure CAD/mesh checks do not establish physical printed fit.

Source: [JLCPCB fabrication capabilities](https://jlcpcb.com/capabilities/pcb-capabilities).


## Native product-view revision 1.1.0

Freshly rebuilt from `assembly.device` with the same pinned native PCB router, caches disabled. All 68 component placements are preserved; the fresh route again has 165 traces, 151 through vias and three bottom ground-pour regions. Netlist, both placement checks, Gerber shorts, default PCB style and the 238-chain continuous style check pass. BOM/CPL remain 62 PCB references; the 16 mechanical assembly parts are excluded.

The native product now includes four printed enclosure solids, panel, flex, two foam supports and eight fasteners, two system diagram pages, and six dimensioned engineering drawing pages. `checks/product-views.json` validates their records and resolved dimensions. The six engineering SVGs use official `circuit-json-to-drawing` 0.0.7, with its documented source-identity adapter and canonical CAD/glTF rotation.

Native explosion collision checking reports incomplete closed-geometry coverage for J1, C28–C31 and the decorative panel image plane. This does not replace the nominal enclosure solid/mesh checks or a physical first print. No prototype hardware or printed-fit validation is claimed.
