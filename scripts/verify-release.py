"""Run independent release gates against a fresh, fully routed native build."""
import hashlib,json,re,shutil,subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'manufacturing/checks';OUT.mkdir(exist_ok=True)
CIRCUIT=ROOT/'dist/index/circuit.json'
CLI=['bun',str(ROOT/'node_modules/.bin/tsci')]
def run(argv,log):
 with (OUT/log).open('w') as f:
  subprocess.run(argv,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,check=True)
 return log

def main():
 data=json.loads(CIRCUIT.read_text())
 diagnostics=[e for e in data if 'error' in e['type'] or 'warning' in e['type']]
 assert not diagnostics,[(e['type'],e.get('message')) for e in diagnostics]
 commands=[
  (CLI+['check','shorts',str(CIRCUIT)],'shorts.txt'),
  (CLI+['check','pcb-style',str(CIRCUIT),'--svg',str(OUT/'pcb-style.svg')],'pcb-style.txt'),
  (['python','scripts/check-continuous-style.py'],'continuous-style.txt'),
 ]
 with ThreadPoolExecutor(max_workers=3) as pool:
  for done in pool.map(lambda job:run(*job),commands):print(done,'PASS',flush=True)
 shutil.copyfile(ROOT/'checks/check-pcb-style/pcb.svg',OUT/'continuous-style.svg')
 for argv,log in [
  (['python','scripts/validate-circuit.py'],'electrical-audit.json'),
  (['python','scripts/validate-reference-labels.py'],'reference-labels-log.txt'),
  (['python','scripts/validate-product.py'],'product-views-log.txt'),
  (['python','scripts/validate-diagnostics.py'],'diagnostics-log.txt'),
  (['python','scripts/audit-routing.py'],'routing-provenance-log.txt'),
 ]:run(argv,log)
 assert 'No shorts detected' in (OUT/'shorts.txt').read_text()
 assert 'No PCB style issues detected' in (OUT/'pcb-style.txt').read_text()
 continuous=(OUT/'continuous-style.txt').read_text()
 assert 'No PCB style issues detected' in continuous
 chains=int(re.search(r'Checking (\d+) continuous chains',continuous)[1])
 review={'result':'PASS','circuit_sha256':hashlib.sha256(CIRCUIT.read_bytes()).hexdigest(),
  'issue_count':0,'long_angled_runs':0,'short_staircases':0,
  'continuous_chain_check':'PASS','continuous_chain_count':chains,
  'physical_clearances_and_shorts':'PASS','rules':'Default unmodified tscircuit PCB style rules',
  'routing':'TSX-authored local power, crystal and ground returns plus fresh built-in native routing; no imported routes'}
 (OUT/'pcb-style-review.json').write_text(json.dumps(review,indent=2)+'\n')
 print(json.dumps({'result':'PASS','default_style_issues':0,'continuous_chains':chains,'diagnostics':0},indent=2))
if __name__=='__main__':main()
