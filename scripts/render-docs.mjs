import { convertCircuitJsonToSchematicSvg, convertCircuitJsonToPcbSvg } from "circuit-to-svg"
import { readFileSync, writeFileSync } from "node:fs"
const circuit = JSON.parse(readFileSync("dist/index/circuit.json", "utf8")).filter(e => !e.type.startsWith("drawing_") && !e.type.startsWith("cad_") && !e.type.startsWith("system_"))
for (const [index, name] of ["usb-power", "rp2354b", "raw-panel", "core-power", "service"].entries()) {
  writeFileSync(`manufacturing/schematic-${index+1}-${name}.svg`, convertCircuitJsonToSchematicSvg(circuit, {schematicSheetId: circuit.find(e => e.type === "schematic_sheet" && e.sheet_index === index+1).schematic_sheet_id, width: 1800, height: 1273, includeVersion: false}))
}
for (const layer of ["top", "bottom"]) {
  writeFileSync(`manufacturing/pcb-${layer}.svg`, convertCircuitJsonToPcbSvg(circuit, {layer, width: 1800, height: 1080, showSolderMask: true, includeVersion: false, shouldDrawErrors: false, shouldDrawWarnings: false, backgroundColor: "#15181b", colorOverrides: {copper: {top: "#c6a66b", bottom: "#bd9f69"}, drill: "#15181b", substrate: "#1c2023", soldermask: {top: "#24282b", bottom: "#24282b"}, soldermaskWithCopperUnderneath: {top: "#303639", bottom: "#303639"}, soldermaskOverCopper: {top: "#303639", bottom: "#303639"}, silkscreen: {top: "#efece1", bottom: "#efece1"}}}))
}
