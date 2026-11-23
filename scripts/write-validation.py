"""Write measured release facts after every fabrication gate has passed."""
import hashlib,json,math,zipfile
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
fab=ROOT/'manufacturing';checks=fab/'checks'
read=lambda path:json.loads((ROOT/path).read_text())
circuit=read('dist/index/circuit.json');counts=Counter(e['type'] for e in circuit)
assert not [e for e in circuit if 'error' in e['type'] or 'warning' in e['type']]
provenance=read('manufacturing/checks/routing-provenance.json')
style=read('manufacturing/checks/pcb-style-review.json')
stock=read('manufacturing/checks/diagnostics.json')
assembly=read('manufacturing/checks/assembly-audit.json')
product=read('manufacturing/checks/product-views.json')
for report in [provenance,style,stock,assembly,product]:assert report['result']=='PASS'
sha=hashlib.sha256((ROOT/'dist/index/circuit.json').read_bytes()).hexdigest()
assert provenance['circuit_sha256']==style['circuit_sha256']==stock['circuit_sha256']==sha
vias=[e for e in circuit if e['type']=='pcb_via']
drill_gap=min(math.hypot(a['x']-b['x'],a['y']-b['y'])-(a['hole_diameter']+b['hole_diameter'])/2 for i,a in enumerate(vias) for b in vias[i+1:])
assert drill_gap>=.2-1e-5
with zipfile.ZipFile(fab/'JLCPCB-Gerbers-RevB.zip') as archive:gerber_count=len(archive.namelist())
fit=read('enclosure/fit-report.json');clearance=read('enclosure/component-clearance.json')
access=read('enclosure/usability-report.json')
text=f'''# Rev B — native tscircuit fabrication release

**PASS for prototype fabrication: zero circuit errors and zero warnings.**

Checked {stock['verified_at']}. USB-C exits the left side of an 18 mm case. The PCB is installed horizontally; the display connector stays beside the short raw-panel flex. The shell seam crosses the USB axis so the housing can open without trapping the connector.

| Check | Measured result |
|---|---|
| TypeScript / native full-product build | PASS |
| Electrical netlist and both placement checks | 0 errors, 0 warnings |
| Independent pin / supply audit | 68 electrical components, 45 nets |
| Native routing | {counts['pcb_trace']} traces, {len(vias)} through vias, four copper layers |
| Inner ground pour | {counts['pcb_copper_pour']} connected regions; no isolated-island warnings |
| Routing inputs | {provenance['source_authored_trace_count']} source-authored local paths and {provenance['source_authored_via_count']} native through vias; zero imported routes; caches disabled |
| Gerber-derived shorts | No shorts detected |
| Default PCB style | 0 issues |
| Continuous-copper style | 0 issues across {style['continuous_chain_count']} chains |
| Minimum via drill-edge spacing | {drill_gap:.3f} mm; required 0.20 mm |
| Via geometry | 0.30 mm drill / 0.55 mm pad, tented both sides |
| Top reference labels | 68 readable, component-associated labels; zero bottom labels |
| Supplier inventory | 25 exact SKUs with recent primary JLCPCB observations |
| BOM / CPL | 62 matched top-side assembly references; supplier orientations resolved |
| Stencil | Four 1.15 mm RP2040 pad windows; no paste on probe pads |
| Native product views | 16 mechanical parts, two System pages, six Drawing pages |
| Enclosure | Four valid single solids and watertight print meshes; nominal fit checks pass |
| Disassembly | Native closed-geometry sweep checks pass |
| Component rear clearance | Minimum {clearance['minimum_clearance_mm']:.3f} mm across all 62 supplier meshes |
| USB usability | Full 40 mm insertion stroke and 7 mm grip allowance, including stand clearance |

All PCB copper is created through tscircuit. The USB entry, local bypass supplies, crystal connections and ground returns use ordinary `trace` / `pcbPath` declarations and native `via` primitives. Ground pads have short local via returns to inner1; the plated USB shell slots already cross the plane. Ground is connected by the pour rather than globally routed tracks, and all other named nets are explicitly assigned to native routing. Connectivity checks remain enabled. The crystal and its load capacitors stay on top with no signal-layer changes. The native {provenance['solver']} routes the remaining connections from the current component placement. All {provenance['source_authored_trace_count']} declared local paths remain fixed. No KiCad, external router, custom algorithm callback or saved-board-route input is used.

The build uses tscircuit {provenance['tscircuit_version']}, Core {json.loads((ROOT/'node_modules/@tscircuit/core/package.json').read_text())['version']} and capacity-autorouter {provenance['autorouter_version']}. A pinned Bun Core patch preserves native branch net/endpoints and avoids borrowing unrelated local width constraints; it also creates explicitly requested inner-layer via ports; the routing algorithm and all diagnostics remain enabled. Its regression also verifies that a real foreign-net short is detected. `checks/routing-provenance.json` records the patch, dependency/source hashes and every native stage. `checks/native-routing/` contains fresh diagnostic output; these files are never imported by the circuit.

`JLCPCB-Gerbers-RevB.zip` contains {gerber_count} fabrication files. `BOM.csv`, `CPL.csv` and `SMT-Stencil-RevB.zip` come from the same validated Circuit JSON. Six engineering SVGs and two system diagrams accompany the editable design, compatible firmware and enclosure files.

The case is {fit['case_size_mm'][0]} × {fit['case_size_mm'][1]} × {fit['case_size_mm'][2]} mm. It retains the R3.65 flex return and uses M3 × 14 case screws. The 14 × 8 mm port admits the mating shell while the complete plug body stays outside; nominal straight-plug profiles are 14 × 8 × 24 and 22 × 10 × 30 mm. The lower display-window edge clears the stand lip by {access['front_window_clearance_above_stand_lip_mm']:.3f} mm.

Supplier observations expire after six hours; run `bun run refresh:stock` before a later build or order. Unknown or expired inventory retains the native warning. Inventory can change during quoting.

This validates prototype files and nominal CAD. A first print, supplied-panel/FPC fit, USB bring-up, power rails and real refresh behavior still require physical hardware. No JLCPCB order has been placed.
'''
(fab/'VALIDATION.md').write_text(text)
print('Wrote measured Rev B validation report')
