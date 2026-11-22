/** Merge coplanar mesh faces with JSCAD, retaining exact boundary vertices. */
import modeling from '@jscad/modeling'
import insertTjunctions from '@jscad/modeling/src/operations/modifiers/insertTjunctions.js'
import {readFileSync,writeFileSync} from 'node:fs'
const file='enclosure/native-solids.json'
const source=JSON.parse(readFileSync(file,'utf8')),out={},parts=[]
for(const [name,operation] of Object.entries(source)){
 const original=modeling.geometries.geom3.create(operation.polygons)
 modeling.geometries.geom3.validate(original)
 const compact=modeling.modifiers.generalize({snap:false,simplify:true,triangulate:false},original)
 compact.polygons=insertTjunctions(compact.polygons)
 modeling.geometries.geom3.validate(compact)
 const volumeDelta=modeling.measurements.measureVolume(compact)-modeling.measurements.measureVolume(original)
 const a=modeling.measurements.measureBoundingBox(original),b=modeling.measurements.measureBoundingBox(compact)
 const boundsDelta=Math.max(...a.flatMap((p,i)=>p.map((v,k)=>Math.abs(v-b[i][k]))))
 if(Math.abs(volumeDelta)>.02 || boundsDelta>.00002)throw Error(name+' geometry changed')
 out[name]={type:'createGeom3',polygons:compact.polygons}
 parts.push({name,original_polygons:original.polygons.length,merged_polygons:compact.polygons.length,volume_delta_mm3:volumeDelta,max_bounds_delta_mm:boundsDelta})
}
writeFileSync(file,JSON.stringify(out)+'\n')
writeFileSync('enclosure/native-solids-audit.json',JSON.stringify({result:'PASS',method:'Native JSCAD coplanar merge; no snapping; original boundary vertices retained',parts},null,2)+'\n')
console.log(parts.map(p=>({name:p.name,before:p.original_polygons,after:p.merged_polygons,volume_delta:p.volume_delta_mm3})))
