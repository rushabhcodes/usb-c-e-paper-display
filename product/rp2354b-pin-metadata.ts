import type { AnyCircuitElement } from "circuit-json"

// The supplier's generated record assigns UART/I2C GPIO functions to the USB
// and dedicated QMI pins. Correct those facts from Raspberry Pi's RP2350
// datasheet, RP2350B pin table and RP2354 stacked-flash section. All electrical
// checks remain enabled; other supplier metadata is preserved.
export function correctRp2354bPinMetadata(elements: AnyCircuitElement[]) {
  const dedicated = new Set([66, 67, 70, 71, 72, 73, 74, 75])
  return elements.map(element => {
    if (element.type !== "source_port" || !dedicated.has(element.pin_number!)) return element
    const corrected = {...element}
    for (const key of Object.keys(corrected)) {
      if (key.startsWith("supports_")) delete (corrected as Record<string, unknown>)[key]
    }
    return {...corrected, is_gpio: false}
  })
}
