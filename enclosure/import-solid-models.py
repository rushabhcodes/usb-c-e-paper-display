"""Tessellate CLI-downloaded supplier STEP solids into closed native GLB models.

Usage: python enclosure/import-solid-models.py /tmp/epaper-closed-model-imports/imports
Download originals with tsci import C165948 / C13585 --jlcpcb --use-exact-footprint --download.
No hole filling, convex hulls, or replacement box geometry is used.
"""
import hashlib,json,sys
from pathlib import Path
import numpy as np
import trimesh
from build123d import import_step

root=Path(__file__).resolve().parent
source=Path(sys.argv[1])
out=root/'component-models';out.mkdir(exist_ok=True)
rows=[]
for sku,filename in [('C165948','TYPE_C_31_M_12'),('C13585','CL31A106KBHNNNE')]:
    origin=np.array([0,-2.7500289000000517,.000010999999999872223] if sku=='C165948' else [0,0,-.65])
    step=source/filename/f'{filename}.step';obj=source/filename/f'{filename}.obj'
    shape=import_step(step)
    assert shape.is_valid
    scene=trimesh.Scene()
    for i,solid in enumerate(shape.solids()):
        vertices,faces=solid.tessellate(.025,.12)
        mesh=trimesh.Trimesh(vertices=np.asarray([tuple(v) for v in vertices]),faces=faces,process=True)
        mesh.update_faces(mesh.nondegenerate_faces());mesh.update_faces(mesh.unique_faces());mesh.merge_vertices(digits_vertex=5)
        assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume>0,(sku,i)
        # Bake the exact existing board-surface origin into the source model.
        # This avoids format-dependent interpretation of a nonzero GLB origin.
        mesh.apply_translation(-origin)
        rgba=[150,157,160,255]
        if solid.color is not None:rgba=[int(255*v) for v in tuple(solid.color)]
        mesh.visual=trimesh.visual.ColorVisuals(mesh,face_colors=rgba)
        scene.add_geometry(mesh,node_name=f'{sku}_solid_{i}')
    original=trimesh.load(obj,force='scene').to_geometry()
    original.apply_translation(-origin)
    assert np.allclose(scene.bounds,original.bounds,atol=.025),(sku,scene.bounds,original.bounds)
    data=scene.export(file_type='glb');path=out/f'{sku}.glb';path.write_bytes(data)
    rows.append({'lcsc':sku,'source':'tsci import --jlcpcb --use-exact-footprint --download',
                 'step_sha256':hashlib.sha256(step.read_bytes()).hexdigest(),
                 'obj_sha256':hashlib.sha256(obj.read_bytes()).hexdigest(),
                 'glb_sha256':hashlib.sha256(data).hexdigest(),'solid_count':len(shape.solids()),
                 'each_mesh_watertight':True,'matches_original_bounds_mm':.025,
                 'source_origin_baked_mm':origin.tolist(),
                 'model_bounds_mm':scene.bounds.tolist(),
                 'model_frame':'native tscircuit GLB loader: CAD Z-up; board-surface origin baked to zero'})
    print(sku,len(shape.solids()),'closed solid meshes',flush=True)
(root/'component-models.json').write_text(json.dumps(rows,indent=2)+'\n')
