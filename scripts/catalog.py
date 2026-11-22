import json,subprocess,sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
queries=sys.argv[1:]
def search(q):
 p=subprocess.run(['bun','run','--bun','tsci','search','--jlcpcb',q,'--json'],capture_output=True,text=True)
 try:
  d=json.loads(p.stdout); Path('docs/parts/'+q+'.json').write_text(json.dumps(d,indent=2)+'\n')
  return q,[{k:c.get(k) for k in ['lcsc','mfr','package','stock','description']} for c in d['results'][:3]]
 except Exception: return q,p.stdout[-200:]+p.stderr[-200:]
with ThreadPoolExecutor(max_workers=4) as pool:
 for q,r in pool.map(search,queries): print(q,json.dumps(r),flush=True)
