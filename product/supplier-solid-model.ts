import solids from "../enclosure/component-models.json"
import { COMPONENT_MODEL_ROOT } from "./model-assets"
import coreInductor from "../enclosure/core-inductor-model.json"

export function supplierSolidModel(sku: string, pcbRotationOffset: number) {
  const record = solids.find(s => s.lcsc === sku)
  if (!record) throw new Error(`Missing validated solid model: ${sku}`)
  const [min,max] = record.model_bounds_mm
  return {glbUrl: sku === "C408335" ? coreInductor.dataUrl : `${COMPONENT_MODEL_ROOT}${sku}.glb`, pcbRotationOffset,
    modelOriginPosition: {x:0,y:0,z:0},modelUnitToMmScale:1,
    modelBounds: {min:{x:min[0],y:min[1],z:min[2]},max:{x:max[0],y:max[1],z:max[2]}}}
}
