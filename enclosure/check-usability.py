"""Check real plug-body insertion and rear finger access against the case solids.

The envelopes are design allowances, not claims that every cable has this size.
The entire swept body is checked, not just a plug drawn at its final position.
"""
import json
from build123d import Compound, Pos, Rot, export_step
from model import (ROOT, OUT, PCB_X, GLASS_REAR, GLASS_W, GLASS_H, GLASS_T,
                   USB_MOUTH_Y, USB_CENTRE_Z, USB_WELL_W, USB_WELL_START,
                   USB_WELL_TOP, block, cyl, case)

parts=case()
stand_pose=Pos(0,0,5)*Rot(-15,0,0)*Pos(0,10.375,71.6)*Rot(90,0,0)
obstacles={n:p for n,p in parts.items() if n!='desk-stand'}
obstacles['glass']=block(GLASS_W,GLASS_H,GLASS_T,z=GLASS_REAR)
profiles=[('ordinary',14,8,24),('large',22,10,30)]
report={'result':'PASS','physical_cable_tested':False,'units':'mm',
        'connector_datum_basis':'C165948 original placed CAD mesh, mm',
        'plug_mating_plane_y':USB_MOUTH_Y,'plug_axis_z':USB_CENTRE_Z,
        'rear_well_width':USB_WELL_W,'checks':[]}
illustration=[]
for name,width,height,length in profiles:
    body=block(width,length,height,PCB_X,USB_MOUTH_Y+length/2,USB_CENTRE_Z-height/2)
    # A straight 40 mm insertion stroke, plus the complete final plug body.
    sweep=block(width,length+40,height,PCB_X,USB_MOUTH_Y+(length+40)/2,USB_CENTRE_Z-height/2)
    intersections={n:round((sweep&p).volume,6) for n,p in obstacles.items()}
    intersections['stand']=round(((stand_pose*sweep)&parts['desk-stand']).volume,6)
    assert max(intersections.values())<.001,(name,intersections)
    report['checks'].append({'profile':name,'body_envelope':[width,height,length],
                            'insertion_travel':40,'intersections_mm3':intersections,
                            'side_clearance_each':(USB_WELL_W-width)/2,
                            'clearance_to_well_ceiling':USB_WELL_TOP-(USB_CENTRE_Z+height/2)})
    if name=='large':illustration.append(body)
# A 14 mm fingertip approaches the plug's rear-facing surface through the open
# rear well, stopping 0.1 mm before the largest plug body. This checks access
# from outside the housing; it is not a claim about hand dexterity.
finger_top=USB_CENTRE_Z-5-.1
finger=cyl(7,finger_top+8,PCB_X,USB_MOUTH_Y+12,-8)
volumes={n:round((finger&p).volume,6) for n,p in obstacles.items()}
assert max(volumes.values())<.001,volumes
report['rear_finger_access']={'diameter':14,'intersections_mm3':volumes}
report['limits']=['Actual cable and first printed fit remain untested.',
                  'The port needs a USB data cable and a compatible USB-host image sender.',
                  'Unusually wide right-angle or locking plugs are outside these envelopes.']
(ROOT/'usability-report.json').write_text(json.dumps(report,indent=2)+'\n')
export_step(Compound(children=list(obstacles.values())+illustration),OUT/'usb-plug-access-assembly.step')
print(json.dumps(report,indent=2))
