#!/usr/bin/env python3
"""Parametric FDM enclosure for PCB Rev B + raw GDEY075T7; dimensions in mm.

Assembly coordinates: X right, Y up when viewing screen, Z rear-to-front.
Case Z=0 is rear exterior. Parts are also exported flat in printing orientation.
"""
import json
import math
from pathlib import Path
from build123d import (Align, Box, Circle, Compound, Cylinder, Plane, Polygon,
                      Pos, RectangleRounded, Rot, extrude, export_step, export_stl)
import trimesh

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "exports"
OUT.mkdir(exist_ok=True)
W,H,CY,R = 182.2,137.2,-3.0,6.0
WALL=2.4
GLASS_W,GLASS_H,GLASS_T = 170.2,111.2,1.25
LAYOUT=json.loads((ROOT.parent/'product/mechanical-layout.json').read_text())
CASE_DEPTH=LAYOUT['case_depth_mm']
CASE_SPLIT=LAYOUT['case_split_z_mm']
STAND_HEIGHT=LAYOUT['stand_height_mm']
CASE_SCREW_LENGTH=LAYOUT['case_screw_length_mm']
GLASS_REAR=CASE_DEPTH-4.15
FACE_Z=CASE_DEPTH-2.4
CARRIER_REAR=GLASS_REAR-3.5
CARRIER_FRONT=CARRIER_REAR+1.5
FPC_CONTACT_Z=9.3-(20.75-CASE_DEPTH)
PCB_X,PCB_Y,PCB_CENTRE_Z=LAYOUT['case_pcb_origin_mm']
PCB_TOP=PCB_CENTRE_Z-.8
FPC_X=-1.05
SCREWS=[(x,y) for x in (-78,78) for y in (-65.8,59.7)]
PCB_HOLES=[(PCB_X+x,PCB_Y-y) for x,y in LAYOUT['pcb_holes_mm']]
# Keep shell support posts clear of the relocated PCB and flex return.
SUPPORTS=[(-72,45),(72,45),(-72,6),(72,-45)]
USB_MOUTH_X=LAYOUT['usb_mouth_case_x_mm']
USB_CENTRE_Y=LAYOUT['usb_axis_case_y_mm']
USB_CENTRE_Z=LAYOUT['usb_axis_case_z_mm']
USB_APERTURE_W,USB_APERTURE_H=LAYOUT['usb_aperture_mm']

def usb_aperture():
    # A small horizontal pill in the left wall. The socket mouth is 0.2 mm
    # proud of the exterior; the complete overmould and fingers stay outside.
    opening=extrude(Plane.YZ*RectangleRounded(USB_APERTURE_W,USB_APERTURE_H,2.1),amount=10)
    return Pos(-96,USB_CENTRE_Y,USB_CENTRE_Z)*opening

def pcb_reference():
    outline=[(PCB_X+x,PCB_Y-y) for x,y in LAYOUT['board_outline_mm']]
    board=Pos(0,0,PCB_TOP)*extrude(Polygon(*outline,align=None),amount=1.6,dir=(0,0,1))
    for x,y in PCB_HOLES:board-=cyl(1.6,3,x,y,PCB_TOP-.5)
    return board

def block(w,h,d,x=0,y=0,z=0):
    return Pos(x,y,z)*Box(w,h,d,align=(Align.CENTER,Align.CENTER,Align.MIN))

def rounded(w,h,r,d,x=0,y=0,z=0):
    return Pos(x,y,z)*extrude(RectangleRounded(w,h,r),amount=d)

def cyl(r,d,x,y,z):
    return Pos(x,y,z)*Cylinder(r,d,align=(Align.CENTER,Align.CENTER,Align.MIN))

def case():
    # Front face prints exterior-down. The rear collar locates the glass laterally.
    face=rounded(W,H,R,2.4,y=CY,z=FACE_Z)
    face-=rounded(165.2,99.92,1.0,4,y=3.15,z=FACE_Z-.35)
    collar=rounded(175.2,116.2,3.0,3.75,z=CARRIER_FRONT)
    collar-=rounded(171.2,112.2,1.0,5,z=CARRIER_FRONT-.6)
    # Open the collar behind the glass for the wide 180-degree FPC return bend.
    collar-=block(20,30,5,FPC_X,-67,CARRIER_FRONT-.6)
    # Split both housing walls through the USB axis. Each half has an open
    # port notch, so the cover and carrier can be installed and removed along Z.
    skirt=rounded(W,H,R,FACE_Z-CASE_SPLIT-.15+.1,y=CY,z=CASE_SPLIT+.15)
    skirt-=rounded(W-2*WALL,H-2*WALL,R-WALL,FACE_Z-CASE_SPLIT+1,y=CY,z=CASE_SPLIT-.25)
    bezel=face+collar+skirt
    for x,y in SCREWS:
        bezel+=cyl(3.2,6.35,x,y,FACE_Z-6.35)
        bezel-=cyl(1.3,7.0,x,y,FACE_Z-6.35) # blind M3 self-tapping pilot, 1.75mm face remaining
    bezel-=usb_aperture()

    # Carrier front is flat; compliant perimeter pads support only opaque glass margins.
    carrier=rounded(174.2,118.2,3.0,1.5,z=CARRIER_REAR)
    carrier-=block(20,30,4,FPC_X,-58,CARRIER_REAR-1.1)
    for x,y in SCREWS:
        carrier-=cyl(3.6,4,x,y,CARRIER_REAR-1.1)
    for x,y in PCB_HOLES:
        carrier+=cyl(3.0,1.0,x,y,PCB_TOP+1.6)
        carrier-=cyl(1.3,2.3,x,y,PCB_TOP+1.6)
    carrier-=usb_aperture()

    rear=rounded(W,H,R,CASE_SPLIT-.15,y=CY)
    rear-=rounded(W-2*WALL,H-2*WALL,R-WALL,FACE_Z+.15,y=CY,z=2.4)
    for x,y in SCREWS:
        # Floor supports the screw head; front-bezel posts receive M3 x 14 screws.
        rear-=cyl(1.7,4,x,y,-.5)
    for x,y in SUPPORTS:
        rear+=cyl(3.2,CARRIER_REAR-2.4,x,y,2.4)
    rear-=usb_aperture()
    for native_x in (-28,-8):
        rear-=cyl(4,4,PCB_X+native_x,PCB_Y+19,-.5)

    # Stable cradle: 15-degree lean, 0.6 mm total slot clearance, closed bottom.
    profile=Plane.YZ*Polygon((-35,0),(35,0),(25,STAND_HEIGHT),(-18,STAND_HEIGHT),align=None)
    stand=Pos(-55,0,0)*extrude(profile,amount=110)
    stand-=Pos(0,0,5)*Rot(-15,0,0)*Box(120,CASE_DEPTH+.6,70,align=(Align.CENTER,Align.CENTER,Align.MIN))
    return {"front-bezel":bezel,"panel-carrier":carrier,"rear-cover":rear,"desk-stand":stand}

def main():
    parts=case()
    printed={
        "front-bezel":Pos(0,0,CASE_DEPTH)*Rot(180,0,0)*parts["front-bezel"],
        "panel-carrier":Pos(0,0,CARRIER_FRONT)*Rot(180,0,0)*parts["panel-carrier"],
        "rear-cover":parts["rear-cover"],"desk-stand":parts["desk-stand"],
    }
    report={"units":"mm","physical_prototype_tested":False,"parts":{}}
    for name,part in parts.items():
        assert part.is_valid and len(part.solids())==1,(name,"invalid/disconnected solid")
        export_step(part,OUT/f"{name}-assembly.step")
        export_step(printed[name],OUT/f"{name}.step")
        export_stl(printed[name],OUT/f"{name}.stl",tolerance=.06,angular_tolerance=.15)
        mesh=trimesh.load_mesh(OUT/f"{name}.stl")
        assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume>0,name
        report["parts"][name]={"valid_solid":True,"watertight":True,
            "single_body":len(part.solids())==1,"volume_mm3":round(part.volume,2),
            "print_size_mm":[round(v,2) for v in mesh.extents]}
    for a,b in [("front-bezel","rear-cover"),("front-bezel","panel-carrier"),("rear-cover","panel-carrier")]:
        volume=(parts[a]&parts[b]).volume
        assert volume<.001,(a,b,volume)
    stand_pose=Pos(0,0,5)*Rot(-15,0,0)*Pos(0,CASE_DEPTH/2,71.6)*Rot(90,0,0)
    for name in ('front-bezel','panel-carrier','rear-cover'):
        assert ((stand_pose*parts[name])&parts['desk-stand']).volume<.001,(name,'stand collision')
    glass=block(GLASS_W,GLASS_H,GLASS_T,z=GLASS_REAR)
    board=pcb_reference()
    export_stl(board,OUT/"pcb-reference-assembly.stl",tolerance=.03,angular_tolerance=.15)
    for name in ("front-bezel","rear-cover","panel-carrier"):
        for label,reference in [("glass",glass),("pcb",board)]:
            collision=(parts[name]&reference).volume
            assert collision<.001,(name,label,collision)
    radius=(GLASS_REAR-FPC_CONTACT_Z)/2
    fpc_length=3.2+math.pi*radius+8.6
    assert fpc_length<24 and radius>3
    # Read anchors from the fabrication circuit, so button/port placement is auditable.
    circuit=json.loads((ROOT.parent/"dist/board/circuit.json").read_text())
    source={e['source_component_id']:e['name'] for e in circuit if e['type']=='source_component'}
    anchors={source[e['source_component_id']]:e.get('footprint_origin',e['center'])
             for e in circuit if e['type']=='pcb_component' and e.get('source_component_id') in source}
    assert anchors['J1']=={'x':-46,'y':0} and anchors['J2']=={'x':38.9,'y':22.3}
    assert anchors['SW1']=={'x':-28,'y':-19} and anchors['SW2']=={'x':-8,'y':-19}
    report.update({"case_size_mm":[W,H,CASE_DEPTH],"glass_pocket_clearance_per_side_mm":.5,
        "glass_front_foam_gap_mm":.5,"glass_back_perimeter_foam_gap_mm":2.0,
        "pcb_top_plane_to_rear_floor_mm":round(PCB_TOP-2.4,3),"pcb_hole_centres":PCB_HOLES,
        "case_screw_centres":SCREWS,"solid_intersections_mm3":0,
        "case_split_z_mm":CASE_SPLIT,"shell_seam_clearance_mm":.3,
        "stand_lean_degrees":15,"stand_height_mm":STAND_HEIGHT,"case_screw_length_mm":CASE_SCREW_LENGTH,"stand_slot_clearance_total_mm":.6,
        "stand_case_intersections_mm3":0,
        "fpc_assumed_contact_plane_z_mm":FPC_CONTACT_Z,"fpc_bend_radius_mm":radius,
        "fpc_estimated_path_mm":round(fpc_length,3),"fpc_nominal_length_mm":24,
        "fpc_minimum_straight_stiffener_mm":6,
        "pcb_case_origin_mm":[PCB_X,PCB_Y,PCB_CENTRE_Z],
        "usb_access":"flush left-side USB-C port; complete plug body outside enclosure",
        "usb_aperture_width_mm":USB_APERTURE_W,"usb_aperture_height_mm":USB_APERTURE_H,
        "usb_mating_plane_x_mm":USB_MOUTH_X,"usb_axis_y_mm":USB_CENTRE_Y,
        "usb_axis_z_mm":USB_CENTRE_Z,"usb_mouth_projection_mm":round(-W/2-USB_MOUTH_X,3),
        "button_centres":[[PCB_X-28,PCB_Y+19],[PCB_X-8,PCB_Y+19]],
        "notes":["FPC contact depth/height and plug overmould require physical fit confirmation.",
                 "No pressure or hard support on active glass area; foam on opaque perimeter only.",
                 "As-built panel and connector tolerances are not established by CAD checks."]})
    (ROOT/'fit-report.json').write_text(json.dumps(report,indent=2)+'\n')
    assembly=Compound(children=[parts[n] for n in ('front-bezel','panel-carrier','rear-cover')]+[glass,board])
    export_step(assembly,OUT/'enclosure-assembly.step')
    for path in OUT.glob("*.step"):path.write_text("\n".join(line.rstrip() for line in path.read_text().splitlines())+"\n")
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
