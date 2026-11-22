"""Check the complete side plug insertion sweep and grip against actual CAD."""
import json,math
from build123d import Compound,Pos,Rot,export_step
from model import (ROOT,OUT,W,CASE_DEPTH,STAND_HEIGHT,GLASS_REAR,GLASS_W,GLASS_H,GLASS_T,
                   USB_MOUTH_X,USB_CENTRE_Y,USB_CENTRE_Z,USB_APERTURE_W,
                   USB_APERTURE_H,block,case)
parts=case()
stand_pose=Pos(0,0,5)*Rot(-15,0,0)*Pos(0,CASE_DEPTH/2,71.6)*Rot(90,0,0)
obstacles={n:p for n,p in parts.items() if n!='desk-stand'}
obstacles['glass']=block(GLASS_W,GLASS_H,GLASS_T,z=GLASS_REAR)
report={'result':'PASS','physical_cable_tested':False,'units':'mm',
 'connector_datum_basis':'C165948 original placed CAD mesh, mm',
 'exit':'left side','plug_mating_plane_x':USB_MOUTH_X,
 'plug_axis_y':USB_CENTRE_Y,'plug_axis_z':USB_CENTRE_Z,
 'socket_projection_beyond_case':round(-W/2-USB_MOUTH_X,3),
 'aperture':[USB_APERTURE_W,USB_APERTURE_H],'checks':[]}
illustration=[]
def check(shape,include_stand=True):
 volumes={n:round((shape&p).volume,6) for n,p in obstacles.items()}
 if include_stand:volumes['stand']=round(((stand_pose*shape)&parts['desk-stand']).volume,6)
 assert max(volumes.values())<.001,volumes
 return volumes
for name,width,height,length in [('ordinary',14,8,24),('large',22,10,30)]:
 body=block(length,width,height,USB_MOUTH_X-length/2,USB_CENTRE_Y,USB_CENTRE_Z-height/2)
 sweep=block(length+40,width,height,USB_MOUTH_X-(length+40)/2,USB_CENTRE_Y,USB_CENTRE_Z-height/2)
 volumes=check(sweep)
 # A mating shell extends 6.65 mm into the socket. Its outer swept section
 # checks the aperture, while electrical mating within the socket is intentional.
 shell=block(6.65+40,8.25,2.56,USB_MOUTH_X+(6.65-40)/2,USB_CENTRE_Y,USB_CENTRE_Z-1.28)
 shell_volumes=check(shell)
 # Grip clearance: add a 7 mm finger envelope above/below the external body.
 grip=block(length+20,width+14,height+14,USB_MOUTH_X-(length+20)/2-.2,USB_CENTRE_Y,USB_CENTRE_Z-height/2-7)
 grip_volumes=check(grip)
 report['checks'].append({'profile':name,'body_envelope':[width,height,length],
  'insertion_travel':40,'body_intersections_mm3':volumes,
  'mating_shell_intersections_mm3':shell_volumes,'grip_intersections_mm3':grip_volumes,
  'body_fully_external':True,'grip_allowance_each_side':7})
 if name=='large':illustration.append(body)
window_clearance=5-math.sin(math.radians(15))*(CASE_DEPTH/2-CASE_DEPTH)+math.cos(math.radians(15))*(71.6+3.15-99.92/2)-STAND_HEIGHT
assert window_clearance>3
report['front_window_clearance_above_stand_lip_mm']=round(window_clearance,3)
report['limits']=['First printed fit and actual cable remain untested.',
 'Use a USB data cable and a compatible USB-host image sender.',
 'The profiles cover straight plugs, not every right-angle or locking cable.']
(ROOT/'usability-report.json').write_text(json.dumps(report,indent=2)+'\n')
export_step(Compound(children=list(obstacles.values())+illustration),OUT/'usb-plug-access-assembly.step')
path=OUT/'usb-plug-access-assembly.step';path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines())+'\n')
print(json.dumps(report,indent=2))
