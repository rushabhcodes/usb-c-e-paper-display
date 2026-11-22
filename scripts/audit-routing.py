"""Verify source-authored tscircuit paths and fresh native routing provenance."""
import hashlib
import json
import argparse
from pathlib import Path

root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--debug-dir',default='dist/native-routing-release-final')
args=parser.parse_args()
debug=root/args.debug_dir
source_files=[root/'index.circuit.tsx',root/'board.circuit.tsx',*sorted((root/'product').glob('*.ts')), *sorted((root/'product').glob('*.tsx'))]
source='\n'.join(p.read_text() for p in source_files)
source_files += [root/'enclosure/native-solids.json',root/'enclosure/viewer-manifest.json']
for forbidden in ['algorithmFn','pcbTracePaths','pcb-routes.json','savedRouter','<pcbtrace','<via ']:
    assert forbidden not in source,f'Non-native routing input: {forbidden}'
assert 'preset: "tscircuit"' in source
meta=json.loads((debug/'board.meta.json').read_text())
phases=meta['phases']
assert phases
for phase in phases:
    assert phase['autorouterName'] in ['tscircuit','bus_lanes','simplify']
    assert phase['cacheStatus']=='disabled'
    assert not phase.get('error'),phase.get('error')
phase=next(p for p in phases if p['autorouterName']=='tscircuit')
srj=json.loads((debug/'phase-0.input.simple-route.json').read_text())
assert srj['layerCount']==2 and srj['allowBlindAndBuriedVias'] is False
circuit_path=root/'dist/index/circuit.json'
circuit=json.loads(circuit_path.read_text())
errors=[e for e in circuit if e['type'].endswith('_error')]
assert not errors,errors[:3]
traces=[e for e in circuit if e['type']=='pcb_trace']
vias=[e for e in circuit if e['type']=='pcb_via']
assert traces and vias
authored_names={'RUN_CHANNEL','DC_CHANNEL','CS_CHANNEL','BUSY_CHANNEL','SCK_CHANNEL'}
authored_sources={e['source_trace_id']:e['name'] for e in circuit
                  if e['type']=='source_trace' and e.get('name') in authored_names}
initial=srj.get('traces',[])
assert len(initial)==len(authored_names)==phases[0]['previousTraceCount']
assert {authored_sources.get(t['source_trace_id']) for t in initial}==authored_names
assert source.count('pcbPaths={')==len(authored_names)
final_by_id={t['pcb_trace_id']:t for t in traces}
clock_output={t['pcb_trace_id']:t for t in json.loads((debug/'phase-0.output.traces.json').read_text())}
def geometry(t):
    keys=['route_type','x','y','layer','width','from_layer','to_layer']
    return [{k:p[k] for k in keys if k in p} for p in t['route']]
refined=[]
for t in initial:
    assert geometry(t)==geometry(clock_output[t['pcb_trace_id']]), 'Clock phase changed an authored path'
    final=final_by_id[t['pcb_trace_id']]
    assert final['source_trace_id']==t['source_trace_id']
    for endpoint in [0,-1]:
        for key in ['x','y','layer']:
            assert t['route'][endpoint][key]==final['route'][endpoint][key], 'Authored endpoint changed'
    if geometry(t)!=geometry(final):refined.append(authored_sources[t['source_trace_id']])
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report={
    'result':'PASS','router':'tscircuit','solver':phase['solverName'],
    'routing_mode':'TSX-authored paths plus built-in native autorouting',
    'existing_trace_count':len(initial),'source_authored_trace_count':len(initial),
    'source_authored_traces':sorted(authored_names),'imported_trace_count':0,
    'source_paths_refined_by_native_router':sorted(refined),
    'cache_status':phase['cacheStatus'],
    'connection_count':phase['connectionCount'],'obstacle_count':phase['obstacleCount'],
    'trace_count':len(traces),'via_count':len(vias),'elapsed_ms':sum(p['elapsedMs'] for p in phases),
    'phases':[{k:p.get(k) for k in ['phaseName','autorouterName','solverName','cacheStatus','previousTraceCount','elapsedMs']} for p in phases],
    'source_sha256':digest(root/'index.circuit.tsx'),'circuit_sha256':digest(circuit_path),
    'source_files_sha256':{str(p.relative_to(root)):digest(p) for p in source_files},
    'config_sha256':digest(root/'tscircuit.config.ts'),
    'routing_input_sha256':digest(debug/'phase-0.input.simple-route.json'),
    'tscircuit_version':json.loads((root/'node_modules/tscircuit/package.json').read_text())['version'],
    'autorouter_version':json.loads((root/'node_modules/@tscircuit/capacity-autorouter/package.json').read_text())['version'],
    'external_router_used':False,'kicad_used':False,'saved_board_routes_used':False,
}
out=root/'manufacturing/checks';out.mkdir(exist_ok=True)
(out/'routing-provenance.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
