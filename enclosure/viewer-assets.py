#!/usr/bin/env python3
"""Export existing validated enclosure geometry into the native PCB CAD frame.

The PCB remains at its fabrication coordinates. The rigid frame change is the
inverse of the case's rotated/flipped PCB installation, in millimetres.
"""
import hashlib
import json
from pathlib import Path
import numpy as np
import trimesh
from PIL import Image
from model import PCB_X, USB_WELL_W

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'models'
OUT.mkdir(exist_ok=True)
# Case coordinates from model.py: PCB centre (-1.05,-8.6,11.3), top toward rear.
CASE_TO_BOARD=np.array([[0,-1,0,-8.6],[-1,0,0,-1.05],[0,0,-1,11.3],[0,0,0,1.]])
# The native GLB importer defaults to CAD Z-up and applies its own (x,z,y)
# loader transform. Retain CAD coordinates in these project model assets.
entries=[]

def color_mesh(mesh,color):
    mesh.visual=trimesh.visual.ColorVisuals(mesh,face_colors=trimesh.visual.color.hex_to_rgba(color))
    return mesh

def box(size,centre):
    m=trimesh.creation.box(size);m.apply_translation(centre);return m

def export(name,label,meshes,color,printed=False):
    scene=trimesh.Scene()
    bounds=[]
    for i,mesh in enumerate(meshes):
        m=mesh.copy()
        if color is not None:color_mesh(m,color)
        m.apply_transform(CASE_TO_BOARD)
        bounds.append(m.bounds)
        scene.add_geometry(m,node_name=f'{name}_{i}',geom_name=f'{name}_{i}')
    data=scene.export(file_type='glb')
    path=OUT/f'{name.lower()}.glb';path.write_bytes(data)
    loaded=trimesh.load(path,force='scene')
    assert np.allclose(loaded.bounds,scene.bounds,atol=2e-5)
    entries.append({'name':name,'label':label,'file':path.name,'printed':printed,
                    'color':color,'bounds_mm':np.array([np.min(np.array(bounds)[:,0],axis=0),np.max(np.array(bounds)[:,1],axis=0)]).round(6).tolist(),
                    'sha256':hashlib.sha256(data).hexdigest()})

for name,label,filename,flip,color in [
 ('BEZEL','Front bezel','front-bezel',20.75,'#263238'),
 ('CARRIER','Panel and PCB carrier','panel-carrier',14.6,'#647d7d'),
 ('REAR','Rear cover','rear-cover',0,'#455a64'),
 ('STAND','15 degree desk cradle','desk-stand',0,'#455a64')]:
    mesh=trimesh.load_mesh(ROOT/'exports'/f'{filename}.stl')
    assert mesh.is_watertight and mesh.is_winding_consistent
    if flip:
        t=trimesh.transformations.rotation_matrix(np.pi,[1,0,0]);t[:3,3]=[0,0,flip];mesh.apply_transform(t)
    if name=='STAND':
        tr=lambda p:trimesh.transformations.translation_matrix(p)
        rx=lambda a:trimesh.transformations.rotation_matrix(np.radians(a),[1,0,0])
        stand_pose=tr([0,0,5])@rx(-15)@tr([0,10.375,71.6])@rx(90)
        mesh.apply_transform(np.linalg.inv(stand_pose))
    export(name,label,[mesh],color,True)

# The display image is a material on the closed glass solid. A separate open
# illustration plane prevented native explosion collision validation.
glass=box([170.2,111.2,1.25],[0,0,17.225])
panel_texture=Image.new('RGB',(1702,1112),'#242724')
panel_texture.paste(Image.open(ROOT.parent/'firmware/examples/dashboard-41.png').convert('RGB').resize((1632,979)),(35,35))
uv=np.column_stack([(glass.vertices[:,0]+85.1)/170.2,(glass.vertices[:,1]+55.6)/111.2])
material=trimesh.visual.material.PBRMaterial(baseColorTexture=panel_texture,metallicFactor=0,roughnessFactor=.95)
glass.visual=trimesh.visual.TextureVisuals(uv=uv,material=material)
assert glass.is_watertight
export('PANEL','GDEY075T7 raw 7.5-inch panel',[glass],None)

# Same 3.65 mm radius / 23.267 mm return path used by model.py and render.py.
points=[[-55.6,16.6],[-58.8,16.6]]
for i in range(1,25):
    a=np.pi*i/24;points.append([-58.8-3.65*np.sin(a),12.95+3.65*np.cos(a)])
points.append([-50.2,9.3]);p=np.asarray(points);tangents=np.gradient(p,axis=0);tangents/=np.linalg.norm(tangents,axis=1)[:,None]
normals=np.column_stack([-tangents[:,1],tangents[:,0]])*.075
verts=[]
for yz,n in zip(p,normals):
    for x,sign in [(-7.3,-1),(5.2,-1),(5.2,1),(-7.3,1)]:verts.append([x,*(yz+sign*n)])
faces=[]
for i in range(len(p)-1):
    for j in range(4):
        a=i*4+j;b=i*4+(j+1)%4;c=(i+1)*4+(j+1)%4;d=(i+1)*4+j
        faces.extend([[a,b,c],[a,c,d]])
faces.extend([[0,2,1],[0,3,2]])
a=(len(p)-1)*4;faces.extend([[a,a+1,a+2],[a,a+2,a+3]])
flex=trimesh.Trimesh(vertices=verts,faces=faces);flex.fix_normals();assert flex.is_watertight
export('FLEX','24-contact panel flex return',[flex],'#c58f32')

# Compressed foam supports stay on the opaque panel perimeter.
def foam_ring(z,thickness,interrupt=False):
    bars=[box([1.5,111.2,thickness],[x,0,z]) for x in [-84.35,84.35]]
    if interrupt:
        # Support only the remaining carrier ledge beside the USB cable well.
        left=PCB_X-USB_WELL_W/2;right=PCB_X+USB_WELL_W/2
        bars += [box([left+83.6,1.5,thickness],[(left-83.6)/2,54.85,z]),
                 box([83.6-right,1.5,thickness],[(right+83.6)/2,54.85,z])]
    else:bars.append(box([167.2,1.5,thickness],[0,54.85,z]))
    if interrupt:
        bars += [box([72.55,1.5,thickness],[-47.325,-54.85,z]),box([74.65,1.5,thickness],[46.275,-54.85,z])]
    else:bars.append(box([167.2,1.5,thickness],[0,-54.85,z]))
    return bars
export('FRONT_FOAM','0.5 mm front perimeter gasket',foam_ring(18.1,.5),'#333333')
export('REAR_FOAM','2 mm rear perimeter support',foam_ring(15.6,2,True),'#333333')

# Nominal pan-head fastener envelopes; threads are not represented.
def screw(z,length):
    shaft=trimesh.creation.cylinder(radius=1.5,height=length,sections=24);shaft.apply_translation([0,0,z+length/2])
    head=trimesh.creation.cylinder(radius=2.8,height=1.6,sections=32);head.apply_translation([0,0,z-.8])
    return [shaft,head]
for i,(x,y) in enumerate([(x,y) for x in (-78,78) for y in (-65.8,59.7)],1):
    meshes=screw(0,16)
    for m in meshes:m.apply_translation([x,y,0])
    export(f'CASE_SCREW_{i}','M3 x 16 case screw',meshes,'#a4adb8')
for i,(x,y) in enumerate([(-1.05-y,-8.6-x) for x in (-45,45) for y in (-25,25)],1):
    meshes=screw(10.5,4)
    for m in meshes:m.apply_translation([x,y,0])
    export(f'PCB_SCREW_{i}','M3 x 4 PCB screw',meshes,'#a4adb8')

# Native polyhedra let tscircuit resolve dimensions from actual solids. The
# pinned drawing-dimension engine cannot measure an external GLB alone.
solids={}
for part in entries:
    if not part['printed']:continue
    mesh=trimesh.load(OUT/part['file'],force='scene').to_geometry()
    assert mesh.is_watertight and mesh.is_winding_consistent
    vertices=mesh.vertices.round(6)
    polygons=[]
    for face in mesh.faces:
        points=vertices[face]
        normal=np.cross(points[1]-points[0],points[2]-points[0]);normal/=np.linalg.norm(normal)
        polygons.append({'vertices':points.tolist(),'plane':[*normal.tolist(),float(normal@points[0])]})
    solids[part['name']]={'type':'createGeom3','polygons':polygons}
(ROOT/'native-solids.json').write_text(json.dumps(solids,separators=(',',':'))+'\n')

report={'units':'mm','case_to_pcb_matrix':CASE_TO_BOARD.tolist(),'parts':entries,
        'source_stl_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'exports').glob('*.stl')},
        'notes':['Viewer meshes derive from the existing print files; PCB copper coordinates are unchanged.',
                 'The cradle is placed using the inverse of the existing 15-degree case pose.',
                 'Fasteners are nominal envelopes; the panel face shows the included example image.',
                 'Physical print, FPC insertion and USB plug fit remain untested.']}
(ROOT/'viewer-manifest.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'models':len(entries),'bytes':sum(p.stat().st_size for p in OUT.glob('*.glb')),'frame':'native PCB CAD coordinates'},indent=2))
