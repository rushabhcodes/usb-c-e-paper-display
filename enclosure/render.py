"""Run with blender --background --python enclosure/render.py (no add-ons)."""
import bpy
import math
from mathutils import Matrix,Vector
from pathlib import Path

ROOT=Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.render.engine='CYCLES';scene.cycles.samples=48
scene.cycles.use_denoising=True
scene.render.resolution_x=1500;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
scene.world.color=(.2,.2,.2)
scene.view_settings.view_transform='AgX'

def mat(name,color,rough=.55):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=rough
    return m
charcoal=mat('Graphite polymer',(.065,.08,.085))
back=mat('Slate polymer',(.16,.20,.21))
carrier_mat=mat('Carrier',(.35,.43,.43))
green=mat('PCB',(.035,.23,.14))
glass_mat=mat('Opaque glass border',(.12,.13,.12))
white=mat('Paper',(.86,.87,.82))
gold=mat('Polyimide flex',(.54,.28,.055),.35)
metal=mat('Connector shields',(.4,.44,.46),.28)

def box(name,location,dimensions,material):
    bpy.ops.mesh.primitive_cube_add(size=1,location=location)
    o=bpy.context.object;o.name=name;o.dimensions=dimensions
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(material);return o

def stl(name,material,flip=0):
    bpy.ops.wm.stl_import(filepath=str(ROOT/'exports'/f'{name}.stl'))
    o=bpy.context.object;o.name=name;o.data.materials.append(material)
    if flip:o.matrix_world=Matrix.Rotation(math.pi,4,'X')@Matrix.Translation((0,0,-flip))
    bevel=o.modifiers.new('Small edge highlights','BEVEL');bevel.width=.18;bevel.segments=2
    return o

parts={
  'bezel':stl('front-bezel',charcoal,20.75),
  'carrier':stl('panel-carrier',carrier_mat,14.6),
  'rear':stl('rear-cover',back),
  'stand':stl('desk-stand',back),
  'glass':box('GDEY075T7 glass',(0,0,17.225),(170.2,111.2,1.25),glass_mat),
  'pcb':box('Rev A PCB',(-1.05,-8.6,11.3),(60,100,1.6),green),
}
# Actual panel active area, with an example image that is also provided to the host sender.
screen=box('Active e-paper',(0,3.15,17.86),(163.2,97.92,.015),white)
texture=bpy.data.materials.new('Example USB image');texture.use_nodes=True
nodes=texture.node_tree.nodes;p=nodes.get('Principled BSDF')
image=nodes.new('ShaderNodeTexImage');image.image=bpy.data.images.load(str(ROOT.parent/'firmware/examples/dashboard-41.png'))
texcoord=nodes.new('ShaderNodeTexCoord');separate=nodes.new('ShaderNodeSeparateXYZ');combine=nodes.new('ShaderNodeCombineXYZ')
texture.node_tree.links.new(texcoord.outputs['Generated'],separate.inputs[0])
texture.node_tree.links.new(separate.outputs['X'],combine.inputs['X'])
texture.node_tree.links.new(separate.outputs['Y'],combine.inputs['Y'])
texture.node_tree.links.new(combine.outputs[0],image.inputs['Vector'])
texture.node_tree.links.new(image.outputs['Color'],p.inputs['Base Color'])
p.inputs['Roughness'].default_value=.85
screen.data.materials.clear();screen.data.materials.append(texture)
parts['screen']=screen
parts['usb']=box('USB-C shield',(-1.05,39.0,8.9),(9,7,3.2),metal)
parts['fpc_connector']=box('FPC connector',(-1.05,-51.6,9.6),(16.9,4.1,1.8),charcoal)
for i,(x,y) in enumerate([(17.95,19.4),(17.95,-.6)]):
    parts[f'button{i}']=box('Service switch',(x,y,9.3),(1.9,5.6,2.4),metal)

# Ribbon path: no twist, straight 3.2 mm neck, 3.65 mm return radius.
points=[(-55.6,16.6),(-58.8,16.6)]
for i in range(1,25):
    a=math.pi*i/24
    points.append((-58.8-3.65*math.sin(a),12.95+3.65*math.cos(a)))
points.append((-50.2,9.3))
verts=[]
for y,z in points:verts.extend([(-7.30,y,z),(5.20,y,z)])
faces=[(i*2,i*2+1,i*2+3,i*2+2) for i in range(len(points)-1)]
mesh=bpy.data.meshes.new('FPC path');mesh.from_pydata(verts,[],faces);mesh.update()
flex=bpy.data.objects.new('24 mm flex return bend',mesh);scene.collection.objects.link(flex)
flex.data.materials.append(gold);flex.modifiers.new('Flex thickness','SOLIDIFY').thickness=.15
parts['flex']=flex

native={k:o.matrix_world.copy() for k,o in parts.items()}
vertical=Matrix.Translation((0,0,5))@Matrix.Rotation(math.radians(-15),4,'X')@Matrix.Translation((0,10.375,71.6))@Matrix.Rotation(math.pi/2,4,'X')
for k,o in parts.items():
    if k!='stand':o.matrix_world=vertical@native[k]

floor=box('Surface',(0,0,-2),(2000,2000,4),mat('Background',(.72,.73,.70)))
def area(name,location,power,size):
    bpy.ops.object.light_add(type='AREA',location=location);o=bpy.context.object;o.name=name
    o.data.energy=power;o.data.shape='DISK';o.data.size=size
    o.rotation_euler=(Vector((0,0,60))-o.location).to_track_quat('-Z','Y').to_euler()
area('Key',(-160,-220,340),1500000,220)
area('Fill',(220,-100,200),700000,180)
area('Rim',(20,180,280),1200000,160)
bpy.ops.object.camera_add(location=(230,-380,225))
camera=bpy.context.object;scene.camera=camera;camera.data.type='ORTHO';camera.data.ortho_scale=260
camera.rotation_euler=(Vector((0,0,72))-camera.location).to_track_quat('-Z','Y').to_euler()
scene.render.filepath=str(ROOT/'assembled.png');bpy.ops.render.render(write_still=True)

offsets={'bezel':58,'glass':35,'screen':35,'carrier':15,'pcb':0,'usb':0,'fpc_connector':0,'button0':0,'button1':0,'rear':-30}
parts['stand'].hide_render=True;parts['flex'].hide_render=True
for k,o in parts.items():
    if k in offsets:o.matrix_world=vertical@Matrix.Translation((0,0,offsets[k]))@native[k]
camera.location=(260,-360,240);camera.data.ortho_scale=320
camera.rotation_euler=(Vector((0,-5,82))-camera.location).to_track_quat('-Z','Y').to_euler()
scene.render.filepath=str(ROOT/'exploded.png');bpy.ops.render.render(write_still=True)
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'enclosure-preview.blend'))
