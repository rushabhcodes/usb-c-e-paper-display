/** Measure the actual native CAD meshes against the thinner rear floor. */
import {loadCadComponentMesh} from 'circuit-json-to-gltf'
import {readFileSync,writeFileSync} from 'node:fs'
const input=process.argv[2]??'dist/index/circuit.json'
const circuit=JSON.parse(readFileSync(input,'utf8'))
const layout=JSON.parse(readFileSync('product/mechanical-layout.json','utf8'))
const source=new Map(circuit.filter(e=>e.type==='source_component').map(e=>[e.source_component_id,e]))
const electrical=new Set(circuit.filter(e=>e.type==='pcb_component').map(e=>e.source_component_id))
const models=circuit.filter(e=>e.type==='cad_component'&&electrical.has(e.source_component_id))
const results=[];let next=0
await Promise.all(Array.from({length:3},async()=>{
 while(next<models.length){
  const original=models[next++],part=source.get(original.source_component_id)
  if(!part?.supplier_part_numbers?.jlcpcb)continue
  const cad={...original},sku=part.supplier_part_numbers.jlcpcb[0]
  if(['C165948','C13585'].includes(sku))cad.model_glb_url='data:model/gltf-binary;base64,'+readFileSync(`enclosure/component-models/${sku}.glb`).toString('base64')
  const mesh=await loadCadComponentMesh(cad)
  if(!mesh?.positions?.length)throw Error(part.name+' has no measurable supplier mesh')
  let maxZ=-Infinity
  for(let i=2;i<mesh.positions.length;i+=3)maxZ=Math.max(maxZ,mesh.positions[i])
  const rearZ=layout.case_pcb_origin_mm[2]-maxZ,clearance=rearZ-2.4
  if(clearance<1.5)throw Error(`${part.name} rear clearance ${clearance} mm`)
  results.push({name:part.name,minimum_body_case_z_mm:rearZ,rear_floor_clearance_mm:clearance})
 }
}))
if(results.length!==62)throw Error(`Expected 62 supplier models; got ${results.length}`)
results.sort((a,b)=>a.rear_floor_clearance_mm-b.rear_floor_clearance_mm)
writeFileSync('enclosure/component-clearance.json',JSON.stringify({result:'PASS',case_depth_mm:layout.case_depth_mm,rear_floor_mm:2.4,minimum_clearance_mm:results[0].rear_floor_clearance_mm,method:'Official loadCadComponentMesh supplier geometry, native installed coordinate transform',physical_fit_tested:false,components:results},null,2)+'\n')
console.log('62 component bodies checked; minimum rear clearance:',results[0].name,results[0].rear_floor_clearance_mm.toFixed(3),'mm')
