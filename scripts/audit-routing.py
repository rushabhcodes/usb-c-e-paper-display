"""Verify source-authored tscircuit paths and fresh native routing provenance."""
import hashlib
import json
import argparse
import subprocess
from pathlib import Path

root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--debug-dir',default='dist/native-routing-final-release')
args=parser.parse_args()
debug=root/args.debug_dir
source_files=[root/'index.circuit.tsx',root/'board.circuit.tsx',*sorted((root/'product').glob('*.ts')), *sorted((root/'product').glob('*.tsx')), *sorted((root/'imports').glob('*.tsx'))]
source='\n'.join(p.read_text() for p in source_files)
source_files += [root/'product/mechanical-layout.json',root/'enclosure/native-solids.json',root/'enclosure/viewer-manifest.json', root/'enclosure/component-models.json', root/'docs/parts/stock-snapshot.json',root/'package.json',root/'bun.lock',*sorted((root/'patches').glob('*.patch'))]
for forbidden in ['algorithmFn','pcbTracePaths','pcb-routes.json','savedRouter','<pcbtrace']:
    assert forbidden not in source,f'Non-native routing input: {forbidden}'
assert 'preset: "tscircuit"' in source
assert '<via ' in source
meta=json.loads((debug/'board.meta.json').read_text())
phases=meta['phases']
assert phases
for phase in phases:
    assert phase['autorouterName'] in ['tscircuit','bus_lanes','tscircuit_simplify']
    assert phase['cacheStatus']=='disabled'
    assert not phase.get('error'),phase.get('error')
phase=next(p for p in phases if p['autorouterName']=='tscircuit')
input_path=debug/f"phase-{phases[0]['routingPhaseIndex'] if phases[0]['routingPhaseIndex'] is not None else 0}.input.simple-route.json"
srj=json.loads(input_path.read_text())
assert srj['layerCount']==4 and srj['allowBlindAndBuriedVias'] is False
circuit_path=root/'dist/index/circuit.json'
circuit=json.loads(circuit_path.read_text())
errors=[e for e in circuit if e['type'].endswith('_error')]
assert not errors,errors[:3]
traces=[e for e in circuit if e['type']=='pcb_trace']
vias=[e for e in circuit if e['type']=='pcb_via']
assert traces and vias
manual_vias=[e for e in circuit if e['type']=='source_manually_placed_via']
assert len(manual_vias)==75
ground=next(e['source_net_id'] for e in circuit if e['type']=='source_net' and e['name']=='GND')
assert len([e for e in manual_vias if e['source_net_id']==ground])==52
busy=next(e['source_net_id'] for e in circuit if e['type']=='source_net' and e['name']=='EPD_BUSY')
assert len([e for e in manual_vias if e['source_net_id']==busy])==2
initial=srj.get('traces',[])
ground_names=['C7_GND','C8_GND','C9_GND','C10_GND','C11_GND','C12_GND','C13_GND','C14_GND','C15_GND','C16_GND','C17_GND','C18_GND','C20_GND','C21_GND','Y1_CASE_2','Y1_CASE_4']
authored_names={'VBUS_ENTRY','FLASH_VCC_DECOUPLING','FLASH_GND_RETURN','FLASH_IC_GND','MCU_EXPOSED_GND','MCU_TESTEN_GND','CRYSTAL_DRIVE','CRYSTAL_LOAD_IN','CRYSTAL_LOAD_OUT','RUN_PULLUP','RUN_SERVICE_LINK'}
authored_names |= {name+'_RETURN' for name in ground_names}
authored_names |= {'MCU_pin'+str(pin) for pin in [1,10,22,33,42,43,44,48,49,23,45,50,20,21,51,52,53,16,24,25,26,11,12,15,17]}
extra=json.loads(subprocess.check_output(['bun','-e','import {extraAuthoredPathNames} from "./product/display-routing"; import {additionalGroundReturns} from "./product/ground-returns"; console.log(JSON.stringify([...extraAuthoredPathNames,...additionalGroundReturns.map(r=>r[0])]))'],cwd=root))
authored_names |= set(extra)
assert len(initial)==len(authored_names)==108==phases[0]['previousTraceCount']
assert 'pcbPaths={' not in source
sources={e['source_trace_id']:e.get('name') for e in circuit if e['type']=='source_trace'}
assert {sources.get(t.get('source_trace_id')) for t in initial}==authored_names
assert all(t.get('isFixed') for t in initial), 'An authored local path is not fixed'
def geometry(t):
 keys=['route_type','x','y','layer','width','from_layer','to_layer']
 return [{k:p[k] for k in keys if k in p} for p in t['route']]
final_by_id={t['pcb_trace_id']:t for t in traces}
for trace in initial:
 assert geometry(trace)==geometry(final_by_id[trace['pcb_trace_id']]), 'Declared power path was altered'
refined=[]
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report={
    'result':'PASS','router':'tscircuit','solver':phase['solverName'],
    'routing_mode':'Source-authored local power, crystal, ground-return and signal paths plus fresh built-in native autorouting',
    'existing_trace_count':len(initial),'source_authored_trace_count':len(initial),
    'source_authored_traces':sorted(authored_names),'imported_trace_count':0,
    'source_authored_via_count':len(manual_vias)+sum(p['route_type']=='via' for t in initial for p in t['route']),
    'source_via_primitive_count':len(manual_vias),'imported_via_count':0,
    'source_paths_refined_by_native_router':sorted(refined),
    'cache_status':phase['cacheStatus'],
    'connection_count':phase['connectionCount'],'obstacle_count':phase['obstacleCount'],
    'trace_count':len(traces),'via_count':len(vias),'elapsed_ms':sum(p['elapsedMs'] for p in phases),
    'phases':[{k:p.get(k) for k in ['phaseName','autorouterName','solverName','cacheStatus','previousTraceCount','elapsedMs','effort']} for p in phases],
    'source_sha256':digest(root/'index.circuit.tsx'),'circuit_sha256':digest(circuit_path),
    'source_files_sha256':{str(p.relative_to(root)):digest(p) for p in source_files},
    'config_sha256':digest(root/'tscircuit.config.ts'),
    'routing_input_sha256':digest(input_path),
    'tscircuit_version':json.loads((root/'node_modules/tscircuit/package.json').read_text())['version'],
    'autorouter_version':json.loads((root/'node_modules/@tscircuit/capacity-autorouter/package.json').read_text())['version'],
    'core_version':json.loads((root/'node_modules/@tscircuit/core/package.json').read_text())['version'],
    'core_patch':'patches/@tscircuit%2Fcore@0.0.2462.patch',
    'external_router_used':False,'kicad_used':False,'saved_board_routes_used':False,
}
out=root/'manufacturing/checks';out.mkdir(exist_ok=True)
(out/'routing-provenance.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
