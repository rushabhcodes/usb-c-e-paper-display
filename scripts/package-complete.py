#!/usr/bin/env python3
"""Package PCB, firmware and printable enclosure together; omit local toolchains."""
import hashlib
import json
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    fab=ROOT/'manufacturing'
    provenance=json.loads((fab/'checks/routing-provenance.json').read_text())
    assert provenance['result']=='PASS' and provenance['router']=='tscircuit'
    assert provenance['existing_trace_count']==provenance['source_authored_trace_count']==5
    assert provenance['imported_trace_count']==0 and provenance['cache_status']=='disabled'
    assert provenance['source_sha256']==digest(ROOT/'index.circuit.tsx')
    for name,expected in provenance['source_files_sha256'].items():
        assert digest(ROOT/name)==expected,name
    assert provenance['config_sha256']==digest(ROOT/'tscircuit.config.ts')
    assert provenance['circuit_sha256']==digest(fab/'design.circuit.json')
    review=json.loads((fab/'checks/pcb-style-review.json').read_text())
    assert review['circuit_sha256']==provenance['circuit_sha256']
    assert review['result']=='PASS' and review['issue_count']==0
    assert review['continuous_chain_check']=='PASS'
    assert 'No shorts detected' in (fab/'checks/shorts.txt').read_text()
    assert json.loads((fab/'checks/electrical-audit.json').read_text())['result']=='PASS'
    entries=[p for p in fab.rglob('*') if p.is_file() and p.name!='SHA256SUMS.txt']
    (fab/'SHA256SUMS.txt').write_text(''.join(f'{digest(p)}  {p.relative_to(fab)}\n' for p in sorted(entries)))
    files=[ROOT/n for n in ['README.md','LICENSE','NOTICE.md','.gitignore','package.json','bun.lock','tsconfig.json','tscircuit.config.json','tscircuit.config.ts','index.circuit.tsx','board.circuit.tsx']]
    for directory in ['product','imports','scripts','manufacturing','firmware','enclosure','docs/parts']:
        files.extend(p for p in (ROOT/directory).rglob('*') if p.is_file() and
                     '__pycache__' not in p.parts and p.suffix not in ['.blend1','.pyc'])
    files.append(ROOT/'docs/reference/README.md')
    files=sorted(set(files))
    checksum=ROOT/'RELEASE-SHA256SUMS.txt'
    checksum.write_text(''.join(f'{digest(p)}  {p.relative_to(ROOT)}\n' for p in files))
    files.append(checksum)
    archive=ROOT/'USB-C-Epaper-RevA-Complete.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in files:z.write(p,str(Path('USB-C-Epaper-RevA')/p.relative_to(ROOT)))
    with zipfile.ZipFile(archive) as z:assert z.testzip() is None
    print(json.dumps({'archive':str(archive),'files':len(files),'bytes':archive.stat().st_size,
                      'sha256':digest(archive),'routing':'TSX-authored paths and fresh local tscircuit; caches disabled'},indent=2))

if __name__=='__main__':main()
