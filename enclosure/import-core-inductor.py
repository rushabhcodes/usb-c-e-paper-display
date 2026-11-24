"""Create a closed GLB from the unmodified TSCI-imported Sunlord STEP solid.

Usage: .toolchains/cad/bin/python enclosure/import-core-inductor.py PATH/TO/imports/MWSA0402S_2R2MT
"""
import base64,hashlib,json,sys
from pathlib import Path
import numpy as np
import trimesh
from build123d import import_step
root=Path(__file__).resolve().parent;source=Path(sys.argv[1]);name='MWSA0402S_2R2MT';sku='C408335'
step=source/(name+'.step');obj=source/(name+'.obj');shape=import_step(step)
assert shape.is_valid
scene=trimesh.Scene()
for i,solid in enumerate(shape.solids()):
 vertices,faces=solid.tessellate(.025,.12)
 mesh=trimesh.Trimesh(vertices=np.asarray([tuple(v) for v in vertices]),faces=faces,process=True)
 mesh.update_faces(mesh.nondegenerate_faces());mesh.update_faces(mesh.unique_faces());mesh.merge_vertices(digits_vertex=5)
 assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume>0
 rgba=[70,75,80,255] if solid.color is None else [int(255*v) for v in tuple(solid.color)]
 mesh.visual=trimesh.visual.ColorVisuals(mesh,face_colors=rgba);scene.add_geometry(mesh,node_name=f'{sku}_solid_{i}')
original=trimesh.load(obj,force='scene').to_geometry()
assert np.allclose(scene.bounds,original.bounds,atol=.025),(scene.bounds,original.bounds)
data=scene.export(file_type='glb');(root/'component-models'/f'{sku}.glb').write_bytes(data)
row={'lcsc':sku,'source':'tsci import --jlcpcb --use-exact-footprint --download','step_sha256':hashlib.sha256(step.read_bytes()).hexdigest(),'obj_sha256':hashlib.sha256(obj.read_bytes()).hexdigest(),'glb_sha256':hashlib.sha256(data).hexdigest(),'solid_count':len(shape.solids()),'each_mesh_watertight':True,'matches_original_bounds_mm':.025,'source_origin_baked_mm':[0,0,0],'model_bounds_mm':scene.bounds.tolist(),'model_frame':'native tscircuit GLB loader: CAD Z-up; supplier board-surface origin unchanged'}
path=root/'component-models.json';rows=json.loads(path.read_text());rows=[r for r in rows if r['lcsc']!=sku]+[row];path.write_text(json.dumps(rows,indent=2)+'\n')
(root/'core-inductor-model.json').write_text(json.dumps({'sha256':row['glb_sha256'],'dataUrl':'data:model/gltf-binary;base64,'+base64.b64encode(data).decode()})+'\n')
print(json.dumps(row,indent=2))
