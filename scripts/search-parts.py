import json, subprocess
from pathlib import Path
queries = ['C20625731','C165948','C262669','C7519','MBR0530','NR3015T100M','C720477','C15849','C15850','C96446','C21120','C23186','C22935','C23187','C25819','C22936','C22962','C25080']
for query in queries:
    proc = subprocess.run(['bun','run','--bun','tsci','search','--jlcpcb',query,'--json'], capture_output=True,text=True)
    try:
        data=json.loads(proc.stdout)
        Path(f'docs/parts/{query}.json').write_text(json.dumps(data,indent=2)+'\n')
        print(query, json.dumps([{k:c.get(k) for k in ['lcsc','mfr','package','stock','description']} for c in data.get('results',[])[:2]]),flush=True)
    except Exception:
        print(query,proc.stdout[-250:],proc.stderr[-250:],flush=True)
