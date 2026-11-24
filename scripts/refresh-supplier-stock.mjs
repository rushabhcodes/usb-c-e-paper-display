import { readFileSync, writeFileSync } from "node:fs"
import { fetchJlcStock } from "../product/supplier-stock"
const circuit=JSON.parse(readFileSync(process.argv[2]??"manufacturing/design.circuit.json","utf8"))
const skus=[...new Set(circuit.flatMap((e)=>e.type==="source_component" ? e.supplier_part_numbers?.jlcpcb??[] : []))].sort()
const records = {}
for(let i=0;i<skus.length;i+=3){
  await Promise.all(skus.slice(i,i+3).map(async sku=>{
    records[sku]=await fetchJlcStock(sku)
    console.log(sku,records[sku].stock,"supplier warehouse units")
  }))
}
writeFileSync("docs/parts/stock-snapshot.json",JSON.stringify(records,null,2)+"\n")
console.log("Verified",skus.length,"supplier SKUs; inventory may change before ordering.")
