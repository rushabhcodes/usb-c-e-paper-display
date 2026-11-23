# Rev B — native tscircuit fabrication release

**PASS for prototype fabrication: zero circuit errors and zero warnings.**

Checked 2026-11-23T08:44:45.908186+00:00. USB-C exits the left side of an 18 mm case. The PCB is installed horizontally; the display connector stays beside the short raw-panel flex. The shell seam crosses the USB axis so the housing can open without trapping the connector.

| Check | Measured result |
|---|---|
| TypeScript / native full-product build | PASS |
| Electrical netlist and both placement checks | 0 errors, 0 warnings |
| Independent pin / supply audit | 68 electrical components, 45 nets |
| Native routing | 185 traces, 136 through vias, four copper layers |
| Inner ground pour | 1 connected regions; no isolated-island warnings |
| Routing inputs | 108 source-authored local paths and 87 native through vias; zero imported routes; caches disabled |
| Gerber-derived shorts | No shorts detected |
| Default PCB style | 0 issues |
| Continuous-copper style | 0 issues across 200 chains |
| Minimum via drill-edge spacing | 0.402 mm; required 0.20 mm |
| Via geometry | 0.30 mm drill / 0.55 mm pad, tented both sides |
| Top reference labels | 68 readable, component-associated labels; zero bottom labels |
| Supplier inventory | 25 exact SKUs with recent primary JLCPCB observations |
| BOM / CPL | 62 matched top-side assembly references; supplier orientations resolved |
| Stencil | Four 1.15 mm RP2040 pad windows; no paste on probe pads |
| Native product views | 16 mechanical parts, two System pages, six Drawing pages |
| Enclosure | Four valid single solids and watertight print meshes; nominal fit checks pass |
| Disassembly | Native closed-geometry sweep checks pass |
| Component rear clearance | Minimum 2.099 mm across all 62 supplier meshes |
| USB usability | Full 40 mm insertion stroke and 7 mm grip allowance, including stand clearance |

All PCB copper is created through tscircuit. The USB entry, local bypass supplies, crystal connections and ground returns use ordinary `trace` / `pcbPath` declarations and native `via` primitives. Ground pads have short local via returns to inner1; the plated USB shell slots already cross the plane. Ground is connected by the pour rather than globally routed tracks, and all other named nets are explicitly assigned to native routing. Connectivity checks remain enabled. The crystal and its load capacitors stay on top with no signal-layer changes. The native AutoroutingPipelineSolver9_PreloadedTraceGraph routes the remaining connections from the current component placement. All 108 declared local paths remain fixed. No KiCad, external router, custom algorithm callback or saved-board-route input is used.

The build uses tscircuit 0.0.3285, Core 0.0.2462 and capacity-autorouter 0.0.1159. A pinned Bun Core patch preserves native branch net/endpoints and avoids borrowing unrelated local width constraints; it also creates explicitly requested inner-layer via ports; the routing algorithm and all diagnostics remain enabled. Its regression also verifies that a real foreign-net short is detected. `checks/routing-provenance.json` records the patch, dependency/source hashes and every native stage. `checks/native-routing/` contains fresh diagnostic output; these files are never imported by the circuit.

`JLCPCB-Gerbers-RevB.zip` contains 13 fabrication files. `BOM.csv`, `CPL.csv` and `SMT-Stencil-RevB.zip` come from the same validated Circuit JSON. Six engineering SVGs and two system diagrams accompany the editable design, compatible firmware and enclosure files.

The case is 182.2 × 137.2 × 18.0 mm. It retains the R3.65 flex return and uses M3 × 14 case screws. The 14 × 8 mm port admits the mating shell while the complete plug body stays outside; nominal straight-plug profiles are 14 × 8 × 24 and 22 × 10 × 30 mm. The lower display-window edge clears the stand lip by 5.275 mm.

Supplier observations expire after six hours; run `bun run refresh:stock` before a later build or order. Unknown or expired inventory retains the native warning. Inventory can change during quoting.

This validates prototype files and nominal CAD. A first print, supplied-panel/FPC fit, USB bring-up, power rails and real refresh behavior still require physical hardware. No JLCPCB order has been placed.
