# 18 mm enclosure validation

The case is **182.2 × 137.2 × 18.0 mm**, 2.75 mm (13.25%) thinner than the previous 20.75 mm housing. USB-C exits the left edge. The shell separates through the socket axis, so either half can be removed without trapping the port.

| Check | Result |
|---|---|
| Four printed parts | Valid single CAD solids and watertight STL meshes |
| Nominal glass, PCB and case intersections | 0 mm³ |
| Supplier component bodies | All 62 checked; minimum rear-floor clearance 2.099 mm |
| Straight plug insertion | Ordinary and large overmoulds clear a 40 mm insertion sweep |
| Cable grip | 7 mm finger envelope around the plug; clears the stand |
| Native tscircuit assembly | 16 mechanical parts; closed geometry for all parts |
| Assembly disassembly | Native collision checks passed with routing disabled |
| Engineering drawing | Six native drawing pages; 18 mm overall depth |

The native geometry preflight used `tsci build index.circuit.tsx --routing-disabled` and reported no errors or warnings. It validates the mechanical assembly, not PCB routing. The revised four-layer PCB is still undergoing routing validation and has no fabrication approval from this report.

The enclosure has not yet been printed or physically fitted. The actual display flex, socket insertion depth and cable should be checked on the first prototype. See `fit-report.json`, `usability-report.json`, `component-clearance.json` and the assembly instructions in `README.md`.
