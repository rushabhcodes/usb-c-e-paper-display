"""Validate the native product views and their real geometry references."""
import hashlib,json
from pathlib import Path
from collections import Counter
root=Path(__file__).resolve().parents[1]
data=json.loads((root/'dist/index/circuit.json').read_text())
counts=Counter(x['type'] for x in data)
manifest=json.loads((root/'enclosure/viewer-manifest.json').read_text())
parts={x['name']:x for x in data if x['type']=='source_component' and x['ftype'] in ['printedpart','subassembly']}
assert set(parts)=={p['name'] for p in manifest['parts']} and len(parts)==16
assert sum(x['ftype']=='printedpart' for x in parts.values())==4
cad={x['source_component_id']:x for x in data if x['type']=='cad_component'}
for part in manifest['parts']:
 assert parts[part['name']]['source_component_id'] in cad
 assert (root/'enclosure/models'/part['file']).is_file()
assert counts['system_block_page']==2
assert counts['system_block_component']==counts['system_block_connection']==16
assert counts['drawing_page']==counts['drawing_page_title_block']==6
assert counts['drawing_part_view']==18 and counts['drawing_dimension_line']==20
assert not [x for x in data if x['type'].endswith('_error')]
texts={x['text'] for x in data if x['type']=='drawing_dimension_line'}
assert {'100 mm','60 mm','90 mm','50 mm','1.6 mm','137.2 mm','182.2 mm','18 mm'} <= texts
pcbids={x['source_component_id'] for x in data if x['type']=='pcb_component'}
assert not pcbids & {p['source_component_id'] for p in parts.values()}
report={'result':'PASS','mechanical_parts':16,'printed_parts':4,'system_pages':2,'drawing_pages':6,'dimension_lines':20,'mechanical_parts_in_pcb_bom':0,'circuit_sha256':hashlib.sha256((root/'dist/index/circuit.json').read_bytes()).hexdigest(),'physical_fit_tested':False,'explosion_geometry_coverage':'Complete closed geometry; actual physical assembly remains untested'}
(root/'manufacturing/checks/product-views.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
