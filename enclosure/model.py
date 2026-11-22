#!/usr/bin/env python3
"""Parametric FDM enclosure for PCB Rev A + raw GDEY075T7; dimensions in mm.

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
GLASS_REAR=16.6
PCB_X,PCB_Y,PCB_TOP = -1.05,-8.6,10.5
FPC_X=PCB_X
SCREWS=[(x,y) for x in (-78,78) for y in (-65.8,59.7)]
PCB_HOLES=[(PCB_X-y,PCB_Y-x) for x in (-45,45) for y in (-25,25)]
SUPPORTS=[(x,y) for x in (-72,72) for y in (-45,45)]

def block(w,h,d,x=0,y=0,z=0):
    return Pos(x,y,z)*Box(w,h,d,align=(Align.CENTER,Align.CENTER,Align.MIN))

def rounded(w,h,r,d,x=0,y=0,z=0):
    return Pos(x,y,z)*extrude(RectangleRounded(w,h,r),amount=d)

def cyl(r,d,x,y,z):
    return Pos(x,y,z)*Cylinder(r,d,align=(Align.CENTER,Align.CENTER,Align.MIN))

def case():
    # Front face prints exterior-down. The rear collar locates the glass laterally.
    face=rounded(W,H,R,2.4,y=CY,z=18.35)
    face-=rounded(165.2,99.92,1.0,4,y=3.15,z=18)
    collar=rounded(175.2,116.2,3.0,3.75,z=14.6)
    collar-=rounded(171.2,112.2,1.0,5,z=14.0)
    # Open the collar behind the glass for the wide 180-degree FPC return bend.
    collar-=block(20,30,5,FPC_X,-67,14)
    bezel=face+collar
    for x,y in SCREWS:
        bezel+=cyl(3.2,6.35,x,y,12.0)
        bezel-=cyl(1.3,7.0,x,y,12.0) # blind M3 self-tapping pilot, 1.75mm face remaining

    # Carrier front is flat; compliant perimeter pads support only opaque glass margins.
    carrier=rounded(174.2,118.2,3.0,1.5,z=13.1)
    carrier-=block(20,30,4,FPC_X,-58,12)
    for x,y in SCREWS:
        carrier-=cyl(3.6,4,x,y,12)
    for x,y in PCB_HOLES:
        carrier+=cyl(3.0,1.0,x,y,12.1)
        carrier-=cyl(1.3,2.3,x,y,12.1)

    rear=rounded(W,H,R,18.35,y=CY)
    rear-=rounded(W-2*WALL,H-2*WALL,R-WALL,18.5,y=CY,z=2.4)
    for x,y in SCREWS:
        # Floor supports the screw head; front-bezel posts receive M3 x 16 screws.
        rear-=cyl(1.7,4,x,y,-.5)
    for x,y in SUPPORTS:
        rear+=cyl(3.2,10.7,x,y,2.4)
    # USB socket faces the upper edge after the physical PCB rotation.
    rear-=block(14,30,8,PCB_X,60,4.9)
    for native_x in (-28,-8):
        rear-=cyl(4,4,PCB_X+19,PCB_Y-native_x,-.5)

    # Stable cradle: 15-degree lean, 0.6 mm total slot clearance, closed bottom.
    profile=Plane.YZ*Polygon((-35,0),(35,0),(25,28),(-18,28),align=None)
    stand=Pos(-55,0,0)*extrude(profile,amount=110)
    stand-=Pos(0,0,5)*Rot(-15,0,0)*Box(120,21.35,70,align=(Align.CENTER,Align.CENTER,Align.MIN))
    return {"front-bezel":bezel,"panel-carrier":carrier,"rear-cover":rear,"desk-stand":stand}

def main():
    parts=case()
    printed={
        "front-bezel":Pos(0,0,20.75)*Rot(180,0,0)*parts["front-bezel"],
        "panel-carrier":Pos(0,0,14.6)*Rot(180,0,0)*parts["panel-carrier"],
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
    stand_pose=Pos(0,0,5)*Rot(-15,0,0)*Pos(0,10.375,71.6)*Rot(90,0,0)
    for name in ('front-bezel','panel-carrier','rear-cover'):
        assert ((stand_pose*parts[name])&parts['desk-stand']).volume<.001,(name,'stand collision')
    glass=block(GLASS_W,GLASS_H,GLASS_T,z=GLASS_REAR)
    board=block(60,100,1.6,PCB_X,PCB_Y,PCB_TOP)
    for name in ("front-bezel","rear-cover","panel-carrier"):
        for label,reference in [("glass",glass),("pcb",board)]:
            collision=(parts[name]&reference).volume
            # Board mounting holes must be represented for the mounting posts.
            if label=="pcb":
                perforated=board
                for x,y in PCB_HOLES:perforated-=cyl(1.6,3,x,y,10)
                collision=(parts[name]&perforated).volume
            assert collision<.001,(name,label,collision)
    radius=(GLASS_REAR-9.3)/2
    fpc_length=3.2+math.pi*radius+8.6
    assert fpc_length<24 and radius>3
    # Read anchors from the fabrication circuit, so button/port placement is auditable.
    circuit=json.loads((ROOT.parent/"manufacturing/design.circuit.json").read_text())
    source={e['source_component_id']:e['name'] for e in circuit if e['type']=='source_component'}
    anchors={source[e['source_component_id']]:e.get('footprint_origin',e['center'])
             for e in circuit if e['type']=='pcb_component' and e.get('source_component_id') in source}
    assert anchors['J1']=={'x':-46,'y':0} and anchors['J2']=={'x':43,'y':0}
    assert anchors['SW1']=={'x':-28,'y':-19} and anchors['SW2']=={'x':-8,'y':-19}
    report.update({"case_size_mm":[W,H,20.75],"glass_pocket_clearance_per_side_mm":.5,
        "glass_front_foam_gap_mm":.5,"glass_back_perimeter_foam_gap_mm":2.0,
        "pcb_component_clearance_to_rear_floor_mm":8.1,"pcb_hole_centres":PCB_HOLES,
        "case_screw_centres":SCREWS,"solid_intersections_mm3":0,
        "stand_lean_degrees":15,"stand_slot_clearance_total_mm":.6,
        "stand_case_intersections_mm3":0,
        "fpc_assumed_contact_plane_z_mm":9.3,"fpc_bend_radius_mm":radius,
        "fpc_estimated_path_mm":round(fpc_length,3),"fpc_nominal_length_mm":24,
        "fpc_minimum_straight_stiffener_mm":6,"usb_opening_mm":[14,8],
        "usb_mouth_recess_mm":round((CY+H/2)-(PCB_Y+50.194),3),
        "button_centres":[[PCB_X+19,PCB_Y+28],[PCB_X+19,PCB_Y+8]],
        "notes":["FPC contact depth/height and plug overmould require physical fit confirmation.",
                 "No pressure or hard support on active glass area; foam on opaque perimeter only.",
                 "As-built panel and connector tolerances are not established by CAD checks."]})
    (ROOT/'fit-report.json').write_text(json.dumps(report,indent=2)+'\n')
    assembly=Compound(children=[parts[n] for n in ('front-bezel','panel-carrier','rear-cover')]+[glass,board])
    export_step(assembly,OUT/'enclosure-assembly.step')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
