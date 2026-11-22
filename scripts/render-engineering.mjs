/** Official drawing exporter with source identities and the documented CAD/glTF frame. */
import { readFileSync, writeFileSync, mkdirSync } from "node:fs"
import { convertCircuitJsonToGltf } from "circuit-json-to-gltf"
import { convertCircuitJsonToDrawingPages } from "@tscircuit/circuit-json-to-drawing"
import { createSceneFromGLTF, loadGLTFWithResourcesFromURL } from "poppygl"
import { mat4 } from "gl-matrix"

const input = process.argv[2] ?? "dist/index/circuit.json"
const out = process.argv[3] ?? "manufacturing/engineering"
const circuit = JSON.parse(readFileSync(input, "utf8"))
const mechanical = new Set(circuit.filter(e => e.type === "source_component" && ["printedpart", "subassembly"].includes(e.ftype)).map(e => e.source_component_id))
const selected = circuit.filter(e => ["pcb_board", "pcb_hole", "pcb_cutout", "source_group"].includes(e.type) || ((e.type === "cad_component" || e.type === "source_component") && mechanical.has(e.source_component_id))).map(e => {
  if (!e.model_glb_url) return e
  const filename = new URL(e.model_glb_url).pathname.split("/").at(-1)
  // Exact immutable project assets, resolved locally so offline exports retain the real geometry.
  const bytes = readFileSync(`enclosure/models/${filename}`)
  return {...e, model_glb_url: `data:model/gltf-binary;base64,${bytes.toString("base64")}`}
})
const bytes = await convertCircuitJsonToGltf(selected, {format:"glb",includeModels:true,drawFauxBoard:false,showBoundingBoxes:false})
if (!(bytes instanceof ArrayBuffer)) throw Error("Expected binary GLB")
const {gltf,resources} = await loadGLTFWithResourcesFromURL("https://fixture.invalid/product.glb", {fetchImpl:async()=>({ok:true,status:200,statusText:"OK",arrayBuffer:async()=>bytes})})
const normalize = mat4.fromYRotation(mat4.create(),Math.PI)
const board = circuit.find(e=>e.type === "pcb_board")
const parts = gltf.nodes.map((node,index)=>{
  const source = node.extras?.tscircuit?.source_component_id
  if (!source && node.name !== "Box0") throw Error(`Unmapped drawing geometry: ${node.name}`)
  const scene = createSceneFromGLTF({...gltf,scene:0,scenes:[{nodes:[index]}]},resources)
  return {...(source?{source_component_id:source}:{pcb_board_id:board.pcb_board_id}),drawCalls:scene.drawCalls.map(dc=>({...dc,model:mat4.multiply(mat4.create(),normalize,dc.model)}))}
})
if (new Set(parts.filter(p=>p.source_component_id).map(p=>p.source_component_id)).size !== 16) throw Error("Missing mechanical geometry")
const pages=await convertCircuitJsonToDrawingPages(circuit,{resolveSceneParts:()=>parts,pixelsPerMm:4,supersampling:2})
mkdirSync(out,{recursive:true})
for(const page of pages){
  const name=circuit.find(e=>e.type === "drawing_page" && e.drawing_page_id===page.drawingPageId).name
  writeFileSync(`${out}/${name}.svg`,page.svg)
  console.log(`${name}.svg`)
}
