"""Check component-side reference identity, readability, and geometric clearance."""
import hashlib,json,math,sys
from pathlib import Path
path=Path(sys.argv[1] if len(sys.argv)>1 else 'dist/index/circuit.json')
data=json.loads(path.read_text())
source={e['source_component_id']:e['name'] for e in data if e['type']=='source_component'}
parts={source[e['source_component_id']]:e for e in data if e['type']=='pcb_component' and e.get('source_component_id') in source}
def bounds(x,y,w,h):return (x-w/2,y-h/2,x+w/2,y+h/2)
def gap(a,b):return math.hypot(max(a[0]-b[2],b[0]-a[2],0),max(a[1]-b[3],b[1]-a[3],0))
def text_bounds(t):
 p=t['anchor_position'];f=t['font_size']
 return bounds(p['x'],p['y'],len(t['text'])*f*.6+.1,f+.1)
labels=[e for e in data if e['type']=='pcb_silkscreen_text' and e['text'] in parts]
assert len(labels)==len(parts)==76
assert len({e['text'] for e in labels})==76
minimum=100
for label in labels:
 name=label['text'];part=parts[name]
 assert label['layer']==part['layer']=='top',name
 assert label.get('pcb_component_id')==part['pcb_component_id'],name
 assert label['ccw_rotation']%360==0 and label['font_size']>=1,name
 b=text_bounds(label)
 assert b[0]>-49.7 and b[2]<49.7 and b[1]>-29.7 and b[3]<29.7,name
 for other in parts.values():
  p=other['center'];distance=gap(b,bounds(p['x'],p['y'],other['width'],other['height']))
  assert distance>=.15-1e-6,(name,source[other['source_component_id']],distance)
  minimum=min(minimum,distance)
 for text in data:
  if text['type']!='pcb_silkscreen_text' or text['layer']!='top' or text is label:continue
  assert gap(b,text_bounds(text))>=.10-1e-6,(name,'text overlap',text['text'])
report={'result':'PASS','top_references':76,'bottom_references':0,'minimum_font_height_mm':1,
        'all_references_associated_with_their_components':True,
        'minimum_label_to_component_bounds_mm':round(minimum,4),
        'minimum_required_clearance_mm':.15,'circuit_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
Path('manufacturing/checks/reference-labels.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
