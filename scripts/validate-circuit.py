"""Release audit of generated Circuit JSON against device pin tables.

This complements routing DRC: it catches components silently omitted during
JSX prop validation and checks the datasheet-critical power/boot/panel nets.
"""
import json
import re
import sys
import argparse
import math
from collections import Counter
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('circuit', nargs='?', default='dist/index/circuit.json')
parser.add_argument('--allow-unrouted', action='store_true')
args = parser.parse_args()
path = Path(args.circuit)
data = json.loads(path.read_text())
components = {x['name']: x for x in data if x['type'] == 'source_component'}
expected = {'J1','J2','F1','U1','U2','U3','U4','U5','Y1','SW1','SW2','Q1','L1','D1','D2','D3'}
expected |= {f'C{i}' for i in range(1,32)} | {f'R{i}' for i in range(1,16)} | {f'TP{i}' for i in range(1,7)}
assert set(components) == expected, f'Missing/extra components: {set(components)^expected}'
for name, component in components.items():
    if name.startswith('TP'):
        assert any(x['type']=='pcb_component' and x.get('source_component_id')==component['source_component_id'] and x.get('do_not_place') for x in data), f'{name} must not appear in assembly BOM'
        continue
    sku = component.get('supplier_part_numbers', {}).get('jlcpcb', [])
    assert len(sku) == 1 and re.fullmatch(r'C\d+', sku[0]), f'{name}: invalid supplier SKU {sku}'

parent = {}
def root(x):
    parent.setdefault(x,x)
    if parent[x] != x: parent[x] = root(parent[x])
    return parent[x]
def join(a,b): parent[root(a)] = root(b)
for x in data:
    if x['type'] != 'source_trace': continue
    ids = x.get('connected_source_port_ids', []) + x.get('connected_source_net_ids', [])
    for item in ids[1:]: join(ids[0], item)
ports = {(x['source_component_id'],x['pin_number']):x['source_port_id'] for x in data if x['type']=='source_port' and 'pin_number' in x}
nets = {x['name']:x['source_net_id'] for x in data if x['type']=='source_net'}
def pin(ref, number): return ports[components[ref]['source_component_id'],number]
def on_net(ref, number, net):
    assert root(pin(ref,number)) == root(nets[net]), f'{ref}.{number} is not on {net}'

# Raspberry Pi RP2040 package/power table, independent of schematic aliases.
for number in [1,10,22,33,42,43,44,48,49]: on_net('U1',number,'V3V3')
for number in [23,45,50]: on_net('U1',number,'VCORE')
for number in [19,57]: on_net('U1',number,'GND')
for number,net in {20:'XIN',21:'XOUT',24:'SWCLK',25:'SWDIO',26:'RUN',46:'USB_DM_MCU',47:'USB_DP_MCU',51:'QSPI_SD3',52:'QSPI_SCLK',53:'QSPI_SD0',54:'QSPI_SD2',55:'QSPI_SD1',56:'QSPI_SS'}.items(): on_net('U1',number,net)
# Flash / crystal: IO2 and IO3 are data pins in quad mode, not fixed pullups.
for number,net in {1:'QSPI_SS',2:'QSPI_SD1',3:'QSPI_SD2',4:'GND',5:'QSPI_SD0',6:'QSPI_SCLK',7:'QSPI_SD3',8:'V3V3'}.items(): on_net('U5',number,net)
for number,net in {1:'XIN',2:'GND',3:'XOSC_OUT',4:'GND'}.items(): on_net('Y1',number,net)
# GDEY075T7 datasheet pin table. NC/test/external sensor contacts remain open.
for number,net in {2:'EPD_GDR',3:'EPD_RESE',5:'EPD_VSHR',8:'GND',9:'EPD_BUSY',10:'EPD_RST',11:'EPD_DC',12:'EPD_CS',13:'EPD_SCK',14:'EPD_MOSI',15:'EPD_3V3',16:'EPD_3V3',17:'GND',18:'EPD_VDD',20:'EPD_VSH',21:'EPD_VGH',22:'EPD_VSL',23:'EPD_VGL',24:'EPD_VCOM',25:'GND',26:'GND'}.items(): on_net('J2',number,net)
for number in [1,4,6,7,19]: assert root(pin('J2',number)) not in {root(x) for x in nets.values()}, f'J2.{number} must remain open'
# Regulator isolation, current sense, and rectifier polarities.
for ref,net in [('U3','V3V3'),('U4','EPD_3V3')]:
    for number,target in {1:'VSYS',2:'GND',5:net}.items(): on_net(ref,number,target)
on_net('U4',3,'EPD_EN')
for ref,number,net in [('Q1',1,'EPD_GDR'),('Q1',2,'EPD_RESE'),('Q1',3,'EPD_SW'),('R11',1,'EPD_RESE'),('R11',2,'GND'),('D1',1,'EPD_PUMP'),('D1',2,'EPD_VGL'),('D2',1,'GND'),('D2',2,'EPD_PUMP'),('D3',1,'EPD_VGH'),('D3',2,'EPD_SW')]: on_net(ref,number,net)
assert len({root(nets[n]) for n in ['VBUS','VSYS','V3V3','VCORE','EPD_3V3','GND']}) == 6, 'Supply rails unexpectedly merged'
assert len({root(nets[n]) for n in ['USB_DP','USB_DM','USB_DP_MCU','USB_DM_MCU']}) == 4, 'USB data nets unexpectedly merged'
for ref in ['R1','R2']: assert abs(components[ref]['resistance']-5100) < 0.01
for ref in ['R3','R4']: assert abs(components[ref]['resistance']-27) < 0.01
assert abs(components['R11']['resistance']-0.47) < 0.001
assert components['U1']['supplier_part_numbers']['jlcpcb'] == ['C2040']
assert components['Y1']['supplier_part_numbers']['jlcpcb'] == ['C20625731']
assert len([x for x in data if x['type']=='pcb_hole' and abs(x.get('hole_diameter',x.get('diameter',0))-3.2)<0.01]) == 4, 'Mounting holes missing'
errors = [x for x in data if x['type'].endswith('_error')]
assert not errors, '\n'.join(x.get('message',x['type']) for x in errors)
counts = Counter(x['type'] for x in data)
if not args.allow_unrouted:
    assert counts['pcb_trace'] > 0, 'No routing present'
    vias = [x for x in data if x['type']=='pcb_via']
    assert vias, 'Plane drops / signal transitions missing'
    board=next(x for x in data if x['type']=='pcb_board')
    expected_layers={'top','bottom'} if board['num_layers']==2 else {'top','inner1','inner2','bottom'}
    for v in vias:
        assert set(v['layers']) == expected_layers, 'Non-through via'
        assert v['hole_diameter'] >= .15-1e-6
        assert v['outer_diameter']-v['hole_diameter'] >= .15-1e-6
        assert v.get('tented_on_top',board.get('default_via_tented_on_top')) and v.get('tented_on_bottom',board.get('default_via_tented_on_bottom')), 'Untented via'
    for i,a in enumerate(vias):
        for b in vias[i+1:]:
            gap=math.hypot(a['x']-b['x'],a['y']-b['y'])-(a['hole_diameter']+b['hole_diameter'])/2
            assert gap >= .2-1e-5, f'Drill spacing {gap:.4f} mm'
    for p in [x for x in data if x['type']=='pcb_plated_hole' and x['shape']=='pill']:
        assert max(p['hole_width'],p['hole_height']) >= 2*min(p['hole_width'],p['hole_height'])-1e-5
        ring=min(p['outer_width']-p['hole_width'],p['outer_height']-p['hole_height'])/2
        assert ring >= (.18 if board['num_layers']==2 else .15)-1e-5, 'Plated-slot annular ring too small'
    u1pcb=next(x['pcb_component_id'] for x in data if x['type']=='pcb_component' and x.get('source_component_id')==components['U1']['source_component_id'])
    windows=[x for x in data if x['type']=='pcb_solder_paste' and x.get('pcb_component_id')==u1pcb and abs(x['x']+14)<2 and abs(x['y'])<2]
    assert len(windows)==4 and all(abs(w['width']-1.15)<1e-5 and abs(w['height']-1.15)<1e-5 for w in windows), 'Exposed-pad stencil must have four windows'
    dnp={x['pcb_component_id'] for x in data if x['type']=='pcb_component' and x.get('do_not_place')}
    assert not any(x['type']=='pcb_solder_paste' and x.get('pcb_component_id') in dnp for x in data), 'Paste on an unpopulated probe pad'
print(json.dumps({'result':'PASS','electrical_components':len(components),'assembled_components':62,'source_nets':len(nets),'pcb_traces':counts['pcb_trace'],'pcb_vias':counts['pcb_via'],'copper_pours':counts['pcb_copper_pour'],'schematic_sheets':counts['schematic_sheet']},indent=2))
