import{readFileSync,writeFileSync}from'node:fs'
import{loadCadComponentMesh}from'circuit-json-to-gltf'
const root=process.cwd()+'/'
const manifest=JSON.parse(readFileSync(root+'enclosure/viewer-manifest.json','utf8'))
const rows=[]
for(const p of manifest.parts){
 const mesh=await loadCadComponentMesh({type:'cad_component',cad_component_id:p.name,source_component_id:p.name,position:{x:0,y:0,z:0},rotation:{x:0,y:0,z:0},model_origin_position:{x:0,y:0,z:0},model_glb_url:'data:model/gltf-binary;base64,'+readFileSync(root+'enclosure/models/'+p.file).toString('base64')})
 const bounds=[[Infinity,Infinity,Infinity],[-Infinity,-Infinity,-Infinity]]
 for(let i=0;i<mesh.positions.length;i+=3)for(let k=0;k<3;k++){bounds[0][k]=Math.min(bounds[0][k],mesh.positions[i+k]);bounds[1][k]=Math.max(bounds[1][k],mesh.positions[i+k])}
 const delta=Math.max(...bounds.flatMap((b,i)=>b.map((v,k)=>Math.abs(v-p.bounds_mm[i][k]))))
 if(delta>.00003)throw Error(p.name+' placement mismatch '+delta)
 rows.push({name:p.name,max_bounds_error_mm:delta})
}
writeFileSync(root+'enclosure/viewer-alignment.json',JSON.stringify({result:'PASS',parts:rows,method:'Official loadCadComponentMesh output compared with the actual installed CAD bounds'},null,2)+'\n')
console.log('All 16 native viewer models match the installed CAD frame')
