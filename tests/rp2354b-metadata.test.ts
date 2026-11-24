import { expect, test } from "bun:test"
import type { AnyCircuitElement } from "circuit-json"
import { correctRp2354bPinMetadata } from "../product/rp2354b-pin-metadata"

test("dedicated USB/QMI pins do not inherit supplier-generated GPIO mux functions", () => {
  const ports = [66, 67, 70, 71, 72, 73, 74, 75].map(pin => ({
    type: "source_port", source_port_id: `p${pin}`, source_component_id: "mcu",
    pin_number: pin, name: `pin${pin}`, supports_i2c_scl: true, supports_uart_rx: true,
    is_bidirectional: true,
  })) as AnyCircuitElement[]
  const result = correctRp2354bPinMetadata(ports)
  for (const port of result) {
    expect(port).not.toHaveProperty("supports_i2c_scl")
    expect(port).not.toHaveProperty("supports_uart_rx")
    expect(port).toHaveProperty("is_bidirectional", true)
  }
  expect(ports[0]).toHaveProperty("supports_i2c_scl", true)
})

test("power requirements and real GPIO metadata remain intact", () => {
  const ports = [
    {type:"source_port", source_port_id:"power", source_component_id:"mcu",pin_number:69,
      name:"QSPI_IOVDD",requires_power:true,must_be_connected:true,requires_voltage:3.3},
    {type:"source_port", source_port_id:"gpio", source_component_id:"mcu",pin_number:8,
      name:"GPIO10",supports_spi_sck:true,is_gpio:true},
  ] as AnyCircuitElement[]
  expect(correctRp2354bPinMetadata(ports)).toEqual(ports)
})
