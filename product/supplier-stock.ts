import { getPlatformConfig } from "@tscircuit/eval"
import type { PartAvailability, PartsEngine } from "@tscircuit/props"
import snapshot from "../docs/parts/stock-snapshot.json"

type StockRecord = PartAvailability & {sourceUrl: string}
const verified = snapshot as Record<string, StockRecord>

/** JLCPCB's server-rendered public product record; never use recommendation stock. */
export function parseJlcStock(html: string, sku: string): {stock: number; price: number | null} | undefined {
  const chunks: string[] = []
  for (const match of html.matchAll(/self\.__next_f\.push\((\[.*?\])\)<\/script>/gs)) {
    try {
      const row = JSON.parse(match[1])
      if (typeof row[1] === "string") chunks.push(row[1])
    } catch { /* Incomplete transport records provide no inventory evidence. */ }
  }
  for (const line of chunks.join("").split("\n")) {
    const start = line.indexOf(":{")
    if (start < 0) continue
    try {
      const record = JSON.parse(line.slice(start+1))
      if (record.componentCode !== sku || !Number.isSafeInteger(record.overseasStockCount) || record.overseasStockCount < 0) continue
      return {stock: record.overseasStockCount, price: typeof record.initialPrice === "number" ? record.initialPrice : null}
    } catch { /* Not a standalone product record. */ }
  }
}

export async function fetchJlcStock(sku: string): Promise<StockRecord> {
  if (!/^C\d+$/.test(sku)) throw Error("Invalid JLCPCB part number")
  const sourceUrl = `https://jlcpcb.com/partdetail/${sku}`
  const response = await fetch(sourceUrl, {signal: AbortSignal.timeout(20000),cache:"no-store"})
  if (!response.ok) throw Error(`JLCPCB product lookup failed: ${response.status}`)
  const result = parseJlcStock(await response.text(), sku)
  if (!result) throw Error(`No verified supplier inventory record for ${sku}`)
  return {...result, currency: result.price === null ? null : "USD", checkedAt: new Date().toISOString(), sourceUrl}
}

// Preserve the built-in footprint, orientation, part selection and pin lookup.
// Only unknown catalog inventory may use a recent, primary-supplier observation.
const base = getPlatformConfig().partsEngine!
export const supplierPartsEngine: PartsEngine = {
  ...base,
  findPart: base.findPart.bind(base),
  fetchPartCircuitJson: base.fetchPartCircuitJson?.bind(base),
  async fetchPartAvailability(request) {
    const entry = request.supplierName === "jlcpcb" ? verified[request.supplierPartNumber] : undefined
    const age = typeof entry?.checkedAt === "string" ? Date.now()-Date.parse(entry.checkedAt) : NaN
    if (entry && age >= 0 && age < 6*60*60*1000) return entry
    return base.fetchPartAvailability?.(request) // Unknown or expired inventory keeps the native warning.
  },
}
