# Rev C — 18 mm enclosure validation

The case is 182.2 × 137.2 × 18 mm, with a left-side USB-C opening and separate 15° stand. The RP2354B layout retains the mounting-hole, connector and FPC datums used by the case.

- Four printed parts are valid single CAD solids with watertight STL meshes.
- Nominal glass, PCB and printed-part intersections are zero.
- All 70 assembled supplier meshes were checked against the 2.4 mm rear floor; minimum clearance is 2.099 mm.
- Ordinary and large straight USB plugs clear the 40 mm insertion sweep and 7 mm grip envelope with the stand installed.
- The native tscircuit assembly contains 16 mechanical parts and six dimensioned drawing pages. Its collision and disassembly checks pass without excluded geometry.

The new inductor uses a closed solid tessellated from its unmodified TSCI-imported supplier STEP model; its bounds match the original OBJ to 0.025 mm. No bounding-box replacement is used for clearance validation.

A first print, real cable fit and the actual panel/FPC tolerance stack remain untested.
