import {test,expect} from 'bun:test'
import {parseJlcStock} from '../product/supplier-stock'
const transport=rows=>`<script>self.__next_f.push(${JSON.stringify([1,rows.map((r,i)=>`${i}:${JSON.stringify(r)}\n`).join('')])})</script>`
test('uses the exact supplier SKU, never stock from a recommendation',()=>{
 const html=transport([{componentCode:'C111',overseasStockCount:9999},{componentCode:'C2040',overseasStockCount:17,initialPrice:1.08}])
 expect(parseJlcStock(html,'C2040')).toEqual({stock:17,price:1.08})
})
test('retains a confirmed zero quantity',()=>{
 expect(parseJlcStock(transport([{componentCode:'C2040',overseasStockCount:0}]),'C2040')).toEqual({stock:0,price:null})
})
test('does not invent availability for missing or malformed supplier data',()=>{
 expect(parseJlcStock('<html>Unavailable</html>','C2040')).toBeUndefined()
 expect(parseJlcStock(transport([{componentCode:'C2040',overseasStockCount:null}]),'C2040')).toBeUndefined()
})
