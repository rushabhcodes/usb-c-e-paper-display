#!/usr/bin/env python3
"""Run tscircuit's default style check across continuous copper chains.

Regional rerouting may split a trace into several Circuit JSON records. This
verification-only view joins unbranched same-net wire edges before invoking the
official checker, so record boundaries cannot hide an angle or staircase. It is
never used as a routing input or as a fabrication export.
"""
import argparse
import json
import subprocess
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('circuit',nargs='?',default='dist/index/circuit.json')
args=p.parse_args()
data=json.loads((ROOT/args.circuit).read_text())
parent={}
def root(k):
    parent.setdefault(k,k)
    if parent[k]!=k:parent[k]=root(parent[k])
    return parent[k]
def join(a,b):parent[root(a)]=root(b)
sources={e['source_trace_id']:e for e in data if e['type']=='source_trace'}
for e in sources.values():
    ids=e.get('connected_source_port_ids',[])+e.get('connected_source_net_ids',[])
    for k in ids[1:]:join(ids[0],k)
groups=defaultdict(dict)
for t in data:
    if t['type']!='pcb_trace':continue
    net=t.get('connection_name')
    if net and net.startswith('source_net_'):net=root(net.split('_mst')[0].split('_rip')[0])
    else:
        source=sources.get(t.get('source_trace_id'))
        if source:
            ids=source.get('connected_source_port_ids',[])+source.get('connected_source_net_ids',[])
            net=root(ids[0]) if ids else net
    assert net,f"Cannot identify electrical net for {t['pcb_trace_id']}"
    for a,b in zip(t['route'],t['route'][1:]):
        if a['route_type']!='wire' or b['route_type']!='wire' or a['layer']!=b['layer']:continue
        av=(round(a['x'],6),round(a['y'],6));bv=(round(b['x'],6),round(b['y'],6))
        if av==bv:continue
        key=tuple(sorted((av,bv)))
        groups[(net,a['layer'])].setdefault(key,(float(a['width']),t.get('source_trace_id')))

chains=[]
for (net,layer),edges in groups.items():
    graph=defaultdict(list)
    for a,b in edges:graph[a].append(b);graph[b].append(a)
    visited=set()
    def walk(a,b):
        points=[a];widths=[];source=None
        while True:
            edge=tuple(sorted((a,b)))
            if edge in visited:break
            visited.add(edge);width,source=edges[edge];widths.append(width);points.append(b)
            if len(graph[b])!=2:break
            nxt=next(v for v in graph[b] if v!=a)
            a,b=b,nxt
        if len(points)<2:return
        route=[{'route_type':'wire','x':v[0],'y':v[1],'width':widths[min(i,len(widths)-1)],'layer':layer}
               for i,v in enumerate(points)]
        chains.append({'type':'pcb_trace','pcb_trace_id':f'continuous_chain_{len(chains)}',
                       'connection_name':net,'source_trace_id':source,'route':route})
    for a in graph:
        if len(graph[a])!=2:
            for b in graph[a]:walk(a,b)
    for a,b in edges:walk(a,b) # Remaining cycles.
    assert len(visited)==len(edges)

output=ROOT/'checks/continuous-style.circuit.json'
output.parent.mkdir(exist_ok=True)
output.write_text(json.dumps([e for e in data if e['type']!='pcb_trace']+chains))
print(f'Checking {len(chains)} continuous chains with the default tscircuit rules.',flush=True)
subprocess.run(['bun','run','--bun','tsci','check','pcb-style',str(output)],cwd=ROOT,check=True)
