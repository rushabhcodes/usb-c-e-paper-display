import { assembly } from "@tscircuit/core"
import { Fragment } from "react"

const sheets = [
  {name:"BEZEL",sheet:"02-front-bezel",title:"FRONT BEZEL",note:"Glass pocket 171.2 x 112.2; window 165.2 x 99.92. Four blind 2.6 mm pilots."},
  {name:"CARRIER",sheet:"03-panel-carrier",title:"PANEL / PCB CARRIER",note:"PCB Rev B: four blind 2.6 mm pilots; right lower fastener offset to clear the flex notch. Unbroken upper glass support ledge."},
  {name:"REAR",sheet:"04-rear-cover",title:"REAR COVER",note:"Wall 2.4; case screw pattern 156 x 125.5; four 3.4 mm clearance holes. Left-side USB-C aperture 14 x 8. Rear BOOTSEL / RESET service holes; closed top edge."},
  {name:"STAND",sheet:"05-desk-stand",title:"15 DEGREE DESK CRADLE",note:"Print envelope 110 x 70 x 26. Slot 18.6 wide; 0.6 total case clearance. Print STL sets the bed orientation."},
] as const

const notes = (text:string) => {
  const lines = text.match(/.{1,74}(?:\s|$)/g) ?? [text]
  return lines.map((line,i) => <assembly.drawing.note key={i} paperX={-137} paperY={-73-i*6} fontSize={2.2} text={line.trim()} />)
}

const title = (text:string,index:number) => <assembly.drawing.titleblock title={text}
  identificationNumber={`USB-EPD-B-${String(index).padStart(2,"0")}`} revisionIndex="B"
  dateOfIssue="2026-11-22" creator="Rushabh Patil" legalOwner="Rushabh Patil"
  approvalPerson="PROTOTYPE / FIT UNTESTED" sheetNumber={index} numberOfSheets={6} />

export function EngineeringDrawings() {
  return <>
    <assembly.drawing.stage name="PCB_SUBSTRATE" boardRefs={[".CONTROLLER"]} />
    <assembly.drawing.page name="01-controller-pcb" displayName="Controller PCB dimensions" size="iso_a4">
      <assembly.drawing.partview name="PCB_PLAN" stageRef=".PCB_SUBSTRATE" displayName="PCB PLAN" direction="z+"
        centerX={-65} centerY={22} width={145} height={100}>
        <assembly.drawing.dimension widthOfView />
        <assembly.drawing.dimension heightOfView />
        <assembly.drawing.dimension fromRef=".CONTROLLER .H1" toRef=".CONTROLLER .H3" axis="x" />
        <assembly.drawing.dimension fromRef=".CONTROLLER .H1" toRef=".CONTROLLER .H2" axis="y" />
      </assembly.drawing.partview>
      <assembly.drawing.partview name="PCB_EDGE" stageRef=".PCB_SUBSTRATE" displayName="PCB EDGE" direction="y-"
        centerX={-65} centerY={-34} width={145} height={30}>
        <assembly.drawing.dimension heightOfView />
      </assembly.drawing.partview>
      <assembly.drawing.partview name="PCB_ISO" stageRef=".PCB_SUBSTRATE" displayName="PCB ISOMETRIC" direction="isometric"
        centerX={77} centerY={22} width={115} height={105} />
      {notes("All dimensions mm. 100 x 60 x 1.6 FR-4 envelope; chamfered outline with USB tongue. Mounting holes: (-45,-25), (-45,25), (45,-25), (23,25); diameter 3.2. Four copper layers; 1 oz; ENIG. Use the validated JLCPCB Gerbers.")}
      {title("RP2040 E-PAPER CONTROLLER - MECHANICAL",1)}
    </assembly.drawing.page>
    {sheets.map((sheet,i) => <Fragment key={sheet.name}>
      <assembly.drawing.page name={sheet.sheet} displayName={sheet.title} size="iso_a4">
        <assembly.drawing.partview name={`${sheet.name}_PLAN`} partRef={`.${sheet.name}`} displayName="PLAN" direction="z-"
          centerX={-69} centerY={20} width={122} height={130}>
          <assembly.drawing.dimension widthOfView />
          <assembly.drawing.dimension heightOfView />
        </assembly.drawing.partview>
        <assembly.drawing.partview name={`${sheet.name}_ISO`} partRef={`.${sheet.name}`} displayName="ISOMETRIC" direction="isometric"
          centerX={65} centerY={32} width={120} height={100} />
        <assembly.drawing.partview name={`${sheet.name}_EDGE`} partRef={`.${sheet.name}`} displayName="EDGE" direction="y+"
          centerX={65} centerY={-26} width={120} height={28}>
          <assembly.drawing.dimension heightOfView />
        </assembly.drawing.partview>
        {notes(sheet.note + " Dimensions mm; views auto-fitted. PETG / PLA. First print fit required; use dimension values rather than page scale.")}
        {title(`${sheet.title} - ENGINEERING OUTLINE`,i+2)}
      </assembly.drawing.page>
    </Fragment>)}
    <assembly.drawing.stage name="CASE_OUTLINE" partRefs={[".BEZEL",".CARRIER",".REAR"]} />
    <assembly.drawing.stage name="PRODUCT_COMPLETE" partRefs={[".BEZEL",".CARRIER",".REAR",".PANEL",".FLEX",".STAND",".FRONT_FOAM",".REAR_FOAM"]} boardRefs={[".CONTROLLER"]} />
    <assembly.drawing.page name="06-product-assembly" displayName="Product assembly and parts list" size="iso_a3">
      <assembly.drawing.partview name="PRODUCT_FRONT" stageRef=".CASE_OUTLINE" displayName="CASE OUTLINE" direction="z-"
        centerX={-124} centerY={20} width={132} height={205}>
        <assembly.drawing.dimension widthOfView />
        <assembly.drawing.dimension heightOfView />
      </assembly.drawing.partview>
      <assembly.drawing.partview name="PRODUCT_ISO" stageRef=".PRODUCT_COMPLETE" displayName="ASSEMBLED PRODUCT" direction="isometric"
        centerX={22} centerY={40} width={120} height={130} />
      <assembly.drawing.partview name="PRODUCT_EDGE" stageRef=".CASE_OUTLINE" displayName="CASE DEPTH" direction="y+"
        centerX={22} centerY={-60} width={120} height={35}>
        <assembly.drawing.dimension heightOfView />
      </assembly.drawing.partview>
      {[
        "QTY   MECHANICAL ASSEMBLY",
        "1     Front bezel",
        "1     Panel / PCB carrier",
        "1     Rear cover",
        "1     15 degree desk cradle",
        "1     GDEY075T7 panel + FPC",
        "1     RP2040 controller PCB",
        "4     M3 x 14 case screws",
        "4     M3 x 4 PCB screws",
        "1     0.5 mm front gasket",
        "1     2 mm rear foam support",
      ].map((text,i) => <Fragment key={text}><assembly.drawing.note paperX={92} paperY={120-i*7} fontSize={2.7} text={text} /></Fragment>)}
      <assembly.drawing.note paperX={-195} paperY={-99} fontSize={2.7} text="USB-C exits left above the stand; 22 x 10 x 30 plug body stays outside. Straight 40 mm insertion and grip checked." />
      <assembly.drawing.note paperX={-195} paperY={-106} fontSize={2.7} text="Rear cover: 4 x M3 x 14. PCB to carrier: 4 x M3 x 4. Do not substitute longer PCB screws." />
      <assembly.drawing.note paperX={-195} paperY={-113} fontSize={2.7} text="Front gasket 0.5 mm; rear perimeter support 2 mm, compressed. Keep pressure off active glass and the FPC." />
      <assembly.drawing.note paperX={-195} paperY={-120} fontSize={2.7} text="Case 182.2 x 137.2 x 18.0; nominal flex return R3.65. Disconnect USB before installing or removing the FPC." />
      {title("USB-C E-PAPER DISPLAY - PRODUCT ASSEMBLY",6)}
    </assembly.drawing.page>
  </>
}
