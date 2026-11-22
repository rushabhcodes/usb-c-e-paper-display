import { assembly } from "@tscircuit/core"
import { ControllerBoard } from "./product/controller-board"
import { EnclosureAssembly } from "./product/assembly"
import { SystemDesign } from "./product/system-design"
import { EngineeringDrawings } from "./product/drawings"

export default function UsbCEpaper() {
  return <assembly.device name="USB_EPAPER">
    <ControllerBoard>
      <SystemDesign />
    </ControllerBoard>
    <EnclosureAssembly />
    <EngineeringDrawings />
  </assembly.device>
}
