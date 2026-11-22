import { Fragment } from "react"
import { assembly } from "@tscircuit/core"
import manifest from "../enclosure/viewer-manifest.json"
import solids from "../enclosure/native-solids.json"
import { MODEL_ROOT } from "./model-assets"

export function EnclosureAssembly() {
  return <>
    {manifest.parts.map(part => {
      const [min,max] = part.bounds_mm
      const cadModel = {
        ...(part.printed ? {jscad: solids[part.name as keyof typeof solids]} : {glbUrl: `${MODEL_ROOT}${part.file}`}),
        modelUnitToMmScale: 1,
        modelOriginPosition: {x:0,y:0,z:0},
        modelBounds: {min:{x:min[0],y:min[1],z:min[2]},max:{x:max[0],y:max[1],z:max[2]}},
      }
      return <Fragment key={part.name}>
        {part.printed ? <assembly.printedpart name={part.name} displayName={part.label}
          material="petg" color={part.color ?? undefined} cadModel={cadModel} /> :
          <assembly.part name={part.name} displayName={part.label} cadModel={cadModel}
            purchaseUrls={part.name === "PANEL" ? ["https://www.good-display.com/product/396.html"] : undefined} />}
      </Fragment>
    })}
    <assembly.explosion.stage name="REMOVE_FASTENERS" nextStageRef="OPEN_REAR">
      <assembly.explosion.move targetRef="STAND" offX={90} />
      <assembly.explosion.move targetRefs={["CASE_SCREW_1","CASE_SCREW_2","CASE_SCREW_3","CASE_SCREW_4"]} offZ={70} />
    </assembly.explosion.stage>
    <assembly.explosion.stage name="OPEN_REAR" prevStageRef="REMOVE_FASTENERS" nextStageRef="UNPLUG_PANEL">
      <assembly.explosion.move targetRef="REAR" offZ={50} />
      <assembly.explosion.move targetRefs={["PCB_SCREW_1","PCB_SCREW_2","PCB_SCREW_3","PCB_SCREW_4"]} offZ={15} />
    </assembly.explosion.stage>
    <assembly.explosion.stage name="UNPLUG_PANEL" prevStageRef="OPEN_REAR" nextStageRef="EXPLODED">
      <assembly.explosion.move targetRefs={["BEZEL","FRONT_FOAM"]} offZ={-80} />
      <assembly.explosion.move targetRefs={["PANEL","FLEX"]} offX={20} />
    </assembly.explosion.stage>
    <assembly.explosion.stage name="EXPLODED" prevStageRef="UNPLUG_PANEL">
      <assembly.explosion.move targetRefs={["PANEL","FLEX"]} offZ={-50} />
      <assembly.explosion.move targetRefs={["CARRIER","REAR_FOAM"]} offZ={-20} />
    </assembly.explosion.stage>
  </>
}
