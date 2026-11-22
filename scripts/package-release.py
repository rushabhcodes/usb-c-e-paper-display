"""Separate JLCPCB fabrication, assembly and stencil files; audit assembly data."""
import csv
import io
import json
import zipfile
from pathlib import Path

root = Path('manufacturing')
archive = root/'JLCPCB-Gerbers-RevA.zip'
with zipfile.ZipFile(archive) as z:
    files = {f:z.read(f) for f in z.namelist()}
bom_data = files.pop('bom.csv') if 'bom.csv' in files else (root/'BOM.csv').read_bytes()
cpl_data = files.pop('pick_and_place.csv') if 'pick_and_place.csv' in files else (root/'CPL.csv').read_bytes()
bom = list(csv.DictReader(io.StringIO(bom_data.decode())))
cpl = list(csv.DictReader(io.StringIO(cpl_data.decode())))
data = json.loads(Path('dist/index/circuit.json').read_text())
src = {e['source_component_id']:e for e in data if e['type']=='source_component'}
pcbs = {src[e['source_component_id']]['name']:e for e in data if e['type']=='pcb_component'
        and e.get('source_component_id') in src and not e.get('do_not_place')}
assert len(bom)==len(cpl)==len(pcbs)==62
assert {r['Designator'] for r in bom}=={r['Designator'] for r in cpl}==set(pcbs)
for row in cpl:
    component = pcbs[row['Designator']]
    assert component.get('pin1_location'), f"Missing footprint orientation: {row['Designator']}"
    assert component.get('supplier_pin1_location_map',{}).get('jlcpcb'), f"Missing supplier orientation: {row['Designator']}"
    # The footprint anchor is the placement reference. Asymmetric USB footprints
    # have a bounding-box centre offset from this anchor; that offset is not a
    # placement correction. Preserve the exporter's supplier-aware rotation.
    pos = component.get('footprint_origin',component['center'])
    row['Mid X'] = f"{pos['x']:.6f}"
    row['Mid Y'] = f"{pos['y']:.6f}"
    row['Layer'] = 'Top'
    assert -50<=pos['x']<=50 and -30<=pos['y']<=30
    assert 0<=float(row['Rotation'])<360
for row in bom:
    assert row['JLCPCB Part #']==src[pcbs[row['Designator']]['source_component_id']]['supplier_part_numbers']['jlcpcb'][0]
(root/'BOM.csv').write_bytes(bom_data)
with (root/'CPL.csv').open('w',newline='') as f:
    writer = csv.DictWriter(f,fieldnames=['Designator','Mid X','Mid Y','Layer','Rotation'])
    writer.writeheader()
    writer.writerows(cpl)
with zipfile.ZipFile(root/'SMT-Stencil-RevA.zip','w',zipfile.ZIP_DEFLATED) as z:
    for name in ['F_Paste.gbr','Edge_Cuts.gbr']:
        z.writestr(name,files[name])
files.pop('F_Fab.gbr',None)
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for name,content in files.items(): z.writestr(name,content)
report = {'result':'PASS','assembled_refs':62,'bom_cpl_match':True,
          'all_supplier_codes_match':True,'coordinate_origin':'PCB centre, matching Gerbers; mm',
          'position_reference':'footprint_origin','side':'Top'}
report['all_supplier_orientations_resolved']=True
(root/'checks/assembly-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
