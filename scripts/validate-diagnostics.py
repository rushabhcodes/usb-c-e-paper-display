"""Release gate for actual diagnostics and recent exact-SKU supplier observations."""
import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
path=Path(sys.argv[1] if len(sys.argv)>1 else 'dist/index/circuit.json')
data=json.loads(path.read_text())
errors=[e for e in data if 'error' in e['type']]
warnings=[e for e in data if 'warning' in e['type']]
assert not errors,[(e['type'],e.get('message')) for e in errors]
assert not warnings,[(e['type'],e.get('message')) for e in warnings]
stock=json.loads(Path('docs/parts/stock-snapshot.json').read_text())
parts=[e for e in data if e['type']=='source_component' and e.get('supplier_part_numbers',{}).get('jlcpcb')]
skus={e['supplier_part_numbers']['jlcpcb'][0] for e in parts}
assert len(parts)==70 and len(skus)==28
now=datetime.now(timezone.utc)
for sku in skus:
 row=stock[sku]
 age=(now-datetime.fromisoformat(row['checkedAt'].replace('Z','+00:00'))).total_seconds()
 assert 0<=age<21600,(sku,'supplier observation expired')
 assert row['stock']>0,(sku,'no inventory')
 assert row['sourceUrl']==f'https://jlcpcb.com/partdetail/{sku}'
report={'result':'PASS','error_count':0,'warning_count':0,'assembled_components':70,
 'verified_supplier_skus':28,'minimum_observed_stock':min(stock[s]['stock'] for s in skus),
 'supplier_observation_maximum_age_hours':6,'verified_at':now.isoformat(),
 'circuit_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
 'limits':'Inventory can change before ordering; printed fit and hardware bring-up are untested.'}
Path('manufacturing/checks/diagnostics.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
