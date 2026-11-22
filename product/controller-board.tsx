import { Fragment, type ComponentType, type ReactNode } from "react"
import type { CapacitorProps, ResistorProps, TraceProps } from "@tscircuit/props"
import { CL05B104KO5NNNC } from "../imports/CL05B104KO5NNNC"
import { CL10A105KB8NNNC } from "../imports/CL10A105KB8NNNC"
import { CC0603KRX7R9BB104 } from "../imports/CC0603KRX7R9BB104"
import { CL21A106KAYNNNE } from "../imports/CL21A106KAYNNNE"
import { A_0402CG150J500NT } from "../imports/A_0402CG150J500NT"
import { UMK212BBJ475KG_T } from "../imports/UMK212BBJ475KG_T"
import { CL31A106KBHNNNE } from "../imports/CL31A106KBHNNNE"
import { A_0603WAF5101T5E } from "../imports/A_0603WAF5101T5E"
import { A_0603WAF270JT5E } from "../imports/A_0603WAF270JT5E"
import { A_0402WGF1001TCE } from "../imports/A_0402WGF1001TCE"
import { A_0603WAF1002T5E } from "../imports/A_0603WAF1002T5E"
import { A_0603WAF1004T5E } from "../imports/A_0603WAF1004T5E"
import { TYPE_C_31_M_12 } from "../imports/TYPE_C_31_M_12"
import { FBF05FT_R470_00L } from "../imports/FBF05FT_R470_00L"
import { RP2040 } from "../imports/RP2040"
import { W25Q16JVSNIQ } from "../imports/W25Q16JVSNIQ"
import { AP2112K_3_3TRG1 } from "../imports/AP2112K_3_3TRG1"
import { ABM8_272_T3 } from "../imports/ABM8_272_T3"
import { AFC01_S24FCA_00 } from "../imports/AFC01_S24FCA_00"
import { USBLC6_2SC6 } from "../imports/USBLC6_2SC6"
import { SI1308EDL_T1_GE3 } from "../imports/SI1308EDL_T1_GE3"
import { A_1206L050_33NR } from "../imports/A_1206L050_33NR"
import { TS_1088_AR02016 } from "../imports/TS_1088_AR02016"
import { MBR0530T1G } from "../imports/MBR0530T1G"
import { FHD252012S_100MT } from "../imports/FHD252012S_100MT"


const capacitorParts: Record<string, ComponentType<Omit<CapacitorProps, "capacitance">>> = {
  C1525: CL05B104KO5NNNC,
  C15849: CL10A105KB8NNNC,
  C14663: CC0603KRX7R9BB104,
  C15850: CL21A106KAYNNNE,
  C1548: A_0402CG150J500NT,
  C412634: UMK212BBJ475KG_T,
  C13585: CL31A106KBHNNNE,
}
const resistorParts: Record<string, ComponentType<Omit<ResistorProps, "resistance">>> = {
  C23186: A_0603WAF5101T5E,
  C25190: A_0603WAF270JT5E,
  C11702: A_0402WGF1001TCE,
  C25804: A_0603WAF1002T5E,
  C22935: A_0603WAF1004T5E,
  C382278: FBF05FT_R470_00L,
}

// Physical pin numbers are intentional: they make the datasheet audit explicit.
// Panel: GDEY075T7, UC8179, 800x480, 24-contact / 0.5-mm FPC.
// Manufacturer datasheet: docs/reference/README.md, pin table and circuit (p. 40).
const sheetOf = (section: string) => ["USB", "Power"].includes(section) ? "SHEET_POWER" : ["Panel", "PanelPower", "Boost", "PanelCaps"].includes(section) ? "SHEET_DISPLAY" : "SHEET_MCU"
const net = (name: string) => `net.${name}`

type CapRow = readonly [string, string, string, string, string, number, number, number, string, number, number]
type ResRow = readonly [string, string, string, string, string, string, number, number, number, string, number, number]
type HvCapRow = readonly [string, string, string, string, string, string, number, number, string, number, number]

const caps: readonly CapRow[] = [
  // name, value, package, LCSC, rail, pcbX, pcbY, rotation, section, schX, schY
  ["C1", "1uF", "0603", "C15849", "VBUS", -42, 9, 90, "USB", -4, 3.5],
  ["C2", "100nF", "0603", "C14663", "VBUS", -39, 7, 90, "USB", -2.6, 3.5],
  ["C3", "1uF", "0603", "C15849", "VSYS", -34, 15, 90, "Power", 2, -5.5],
  ["C4", "10uF", "0805", "C15850", "V3V3", -27, 15, 90, "Power", 7, -5.5],
  ["C5", "1uF", "0603", "C15849", "VSYS", 20, -13, 90, "PanelPower", -11, -6],
  ["C6", "10uF", "0805", "C15850", "EPD_3V3", 27, -13, 90, "PanelPower", -7, -6],
  ["C7", "100nF", "0402", "C1525", "V3V3", -17, -5.4, 270, "Decoupling", 3.5, -1.5],
  ["C8", "100nF", "0402", "C1525", "V3V3", -13, -5.4, 270, "Decoupling", 4.9, -1.5],
  ["C9", "100nF", "0402", "C1525", "V3V3", -8.6, 1.2, 0, "Decoupling", 6.3, -1.5],
  ["C10", "100nF", "0402", "C1525", "V3V3", -13, 5.4, 90, "Decoupling", 7.699999999999999, -1.5],
  ["C11", "100nF", "0402", "C1525", "V3V3", -16.6, 5.4, 90, "Decoupling", 9.1, -1.5],
  ["C12", "100nF", "0402", "C1525", "V3V3", -19.6, -0.8, 90, "Decoupling", 3.5, -3.0],
  ["C13", "100nF", "0402", "C1525", "V3V3", -19.6, -2.7, 90, "Decoupling", 4.9, -3.0],
  ["C14", "100nF", "0402", "C1525", "V3V3", -19.5, 4.2, 180, "Decoupling", 6.3, -3.0],
  ["C15", "1uF", "0603", "C15849", "V3V3", -22.6, 5.6, 0, "Decoupling", 7.699999999999999, -3.0],
  ["C16", "1uF", "0603", "C15849", "VCORE", -22.6, 3.7, 0, "Decoupling", 3.5, -5],
  ["C17", "100nF", "0402", "C1525", "VCORE", -8.6, 2.5, 0, "Decoupling", 4.9, -5],
  ["C18", "100nF", "0402", "C1525", "VCORE", -18, -7, 0, "Decoupling", 6.3, -5],
  ["C19", "100nF", "0402", "C1525", "V3V3", -24.8, -3.2, 180, "Decoupling", 9.1, -3.0],
  ["C20", "15pF", "0402", "C1548", "XIN", -7.2, -4.8, 90, "Clock", 3.5, 2.8],
  ["C21", "15pF", "0402", "C1548", "XOSC_OUT", -2.3, -1.4, 270, "Clock", 7, 2.8],
  // Display high-voltage rail capacitors; selected parts are all rated 50 V.
  ["C22", "1uF", "0603", "C15849", "EPD_VSHR", 38, -4.3, 90, "PanelCaps", 1, -5],
  ["C23", "1uF", "0603", "C15849", "EPD_3V3", 38.7, -0.2, 90, "PanelPower", -5.6, -6],
  ["C24", "1uF", "0603", "C15849", "EPD_VDD", 38.7, 3.2, 90, "PanelCaps", 3, -5],
  ["C25", "1uF", "0603", "C15849", "EPD_VCOM", 38.7, 6.6, 90, "PanelCaps", 5, -5],
] as const

const resistors: readonly ResRow[] = [
  ["R1", "5.1k", "0603", "C23186", "CC1", "GND", -42, -7, 90, "USB", -4, -0.5],
  ["R2", "5.1k", "0603", "C23186", "CC2", "GND", -39.5, -7, 90, "USB", -2, -0.5],
  ["R3", "27", "0603", "C25190", "USB_DM", "USB_DM_MCU", -24.7, 1.4, 0, "USB", 3, 2],
  ["R4", "27", "0603", "C25190", "USB_DP", "USB_DP_MCU", -24.7, -0.5, 0, "USB", 3, 0.1],
  ["R5", "1k", "0402", "C11702", "QSPI_SS", "BOOT_N", -25, -10.5, 180, "Flash", -5.5, 2],
  ["R6", "10k", "0603", "C25804", "V3V3", "QSPI_SS", -21, -11, 0, "Flash", -5.0, 4.2],
  ["R7", "1k", "0402", "C11702", "XOUT", "XOSC_OUT", -8.9, 0, 0, "Clock", 8, 5],
  ["R8", "10k", "0603", "C25804", "V3V3", "RUN", -6, -11, 0, "Control", -9, -4],
  ["R9", "10k", "0603", "C25804", "EPD_EN", "GND", 20, -10, 270, "PanelPower", -11, -3.5],
  ["R10", "1M", "0603", "C22935", "EPD_GDR", "GND", 30, -7, 0, "Boost", -6, 2],
  ["R11", "0.47", "0805", "C382278", "EPD_RESE", "GND", 35, -7, 0, "Boost", -3, 2],
  ["R12", "10k", "0603", "C25804", "EPD_3V3", "EPD_CS", 33, -11, 0, "Panel", 3, 3],
  ["R13", "10k", "0603", "C25804", "EPD_3V3", "EPD_RST", 37, -11, 0, "Panel", 5, 3],
  ["R14", "27", "0603", "C25190", "SCK_MCU", "EPD_SCK", -11, -8, 90, "Panel", 4.5, -1.2],
  ["R15", "27", "0603", "C25190", "MOSI_MCU", "EPD_MOSI", -13.5, -8, 90, "Panel", 12, -1.2],
] as const

const highVoltageCaps: readonly HvCapRow[] = [
  ["C26", "4.7uF", "C412634", "0805", "EPD_3V3", "GND", 27, -3, "PanelPower", -4.2, -6],
  ["C27", "4.7uF", "C412634", "0805", "EPD_SW", "EPD_PUMP", 31.5, 0.8, "Boost", -4, 5.5],
  ["C28", "10uF", "C13585", "1206", "EPD_VGH", "GND", 35, 7.2, "PanelCaps", 1, -7],
  ["C29", "10uF", "C13585", "1206", "EPD_VSH", "GND", 35, 13, "PanelCaps", 3, -7],
  ["C30", "10uF", "C13585", "1206", "EPD_VSL", "GND", 30, 12, "PanelCaps", 5, -7],
  ["C31", "10uF", "C13585", "1206", "EPD_VGL", "GND", 30, 19, "PanelCaps", 7, -7],
] as const

// Spell out wire landings on both sides of a via. This keeps the copper
// continuous for the native router, pour generator and fabrication exporter.
// Coordinates are unchanged; this helper does not compute or alter any route.
const withViaLandings = (path: NonNullable<TraceProps["pcbPath"]>) => path.flatMap(point =>
  typeof point !== "string" && point.via
    ? [{x: point.x, y: point.y}, point, {x: point.x, y: point.y}]
    : [point])

export function ControllerBoard({children}: {children?: ReactNode} = {}) {
  return (
    <board name="CONTROLLER" width="100mm" height="60mm" thickness="1.6mm" layers={2}
      title="USB-C E-PAPER / RP2040 / GDEY075T7" borderRadius="2mm"
      fabricatorPreset="jlcpcb_standard" solderMaskColor="black" silkscreenColor="white"
      minTraceWidth="0.15mm" minTraceToPadEdgeClearance="0.10mm"
      minPadEdgeToPadEdgeClearance="0.12mm" minBoardEdgeClearance="0.3mm"
      minViaEdgeToPadEdgeClearance="0.12mm" minTraceToHoleEdgeClearance="0.2mm" minViaHoleEdgeToViaHoleEdgeClearance="0.2mm"
      minViaHoleDiameter="0.15mm" minViaPadDiameter="0.3mm"
      pcbStyle={{viaHoleDiameter: 0.15, viaPadDiameter: 0.3, silkscreenFontSize: 1}}
      defaultViaTenting="both_sides" allowBlindAndBuriedVias={false}
      autorouterVersion="beta_pipeline9" autorouterEffortLevel="1x" routeRemaining={false}
      autorouter={{local: true, preset: "tscircuit", serverCacheEnabled: false}}>
      <schematicsheet name="SHEET_POWER" displayName="USB-C and main power" sheetIndex={1} />
      <schematicsheet name="SHEET_MCU" displayName="RP2040, flash, clock and debug" sheetIndex={2} />
      <schematicsheet name="SHEET_DISPLAY" displayName="7.5-inch raw panel and boost supply" sheetIndex={3} />
      {[
        ["USB", "USB-C / 5 V input"], ["Power", "3.3 V MCU supply"],
        ["MCU", "RP2040"], ["Decoupling", "Local MCU bypass capacitors"],
        ["Flash", "2 MB QSPI / BOOTSEL"], ["Clock", "12 MHz reference"],
        ["Control", "Reset and debug"], ["Panel", "Raw 7.5-inch panel interface"],
        ["PanelPower", "Switched panel supply"], ["Boost", "Panel boost / charge pump"],
        ["PanelCaps", "50 V display rail reservoirs"],
      ].map(([name, displayName]) => <Fragment key={name}><schematicsection name={name} displayName={displayName} /></Fragment>)}

      <net name="GND" isGroundNet routingPhaseIndex={1} />
      <net name="VBUS" isPowerNet nominalTraceWidth="0.4mm" routingPhaseIndex={1} />
      <net name="VSYS" isPowerNet nominalTraceWidth="0.4mm" routingPhaseIndex={1} />
      <net name="V3V3" isPowerNet nominalTraceWidth="0.25mm" routingPhaseIndex={1} />
      <net name="VCORE" isPowerNet nominalTraceWidth="0.2mm" routingPhaseIndex={1} />
      <net name="EPD_3V3" isPowerNet nominalTraceWidth="0.4mm" routingPhaseIndex={1} />
      {["EPD_SW", "EPD_PUMP", "EPD_VGH", "EPD_VGL", "EPD_VSH", "EPD_VSL", "EPD_VCOM", "EPD_VSHR"].map(name =>
        <Fragment key={name}><net name={name} nominalTraceWidth="0.2mm" minTraceClearance="0.12mm" routingPhaseIndex={1} /></Fragment>)}
      {["CC1", "CC2", "USB_DP", "USB_DM", "EPD_EN", "USB_DM_MCU", "USB_DP_MCU",
        "XIN", "XOUT", "QSPI_SD3", "QSPI_SCLK", "QSPI_SD0", "QSPI_SD2", "QSPI_SD1", "QSPI_SS",
        "SWCLK", "SWDIO", "RUN", "EPD_DC", "EPD_CS", "SCK_MCU", "MOSI_MCU", "EPD_RST", "EPD_BUSY",
        "XOSC_OUT", "BOOT_N", "EPD_GDR", "EPD_RESE", "EPD_SCK", "EPD_MOSI", "EPD_VDD"].map(name =>
        <Fragment key={name}><net name={name} routingPhaseIndex={["XIN", "XOUT", "XOSC_OUT"].includes(name) ? 0 : 1} /></Fragment>)}

      <autoroutingphase name="CLOCK" phaseIndex={0} autorouter="bus_lanes"
        minTraceToPadEdgeClearance="0.15mm" />
      <autoroutingphase name="MAIN" phaseIndex={1} autorouter="tscircuit"
        minTraceToPadEdgeClearance="0.15mm" minViaEdgeToPadEdgeClearance="0.15mm"
        minTraceToHoleEdgeClearance="0.22mm" minViaHoleEdgeToViaHoleEdgeClearance="0.22mm" />

      {/* Hand-authored tscircuit copper for the five style-sensitive signals.
          These PCB paths use TP6 (board centre, rotation zero) as their coordinate
          anchor; their endpoints resolve from component port selectors.
          no router output or external board geometry is imported. Other branches
          of RUN / CS and all other nets are solved by the native autorouter. */}
      <trace name="RUN_CHANNEL" from=".U1 > .pin26" to=".TP6 > .pin1" thickness="0.15mm" pcbPathRelativeTo=".TP6 > .pin1"
        pcbPaths={[withViaLandings([".U1 > .pin26", {x: -1.8, y: 1.799844}, ".TP6 > .pin1"])]} />
      <trace name="DC_CHANNEL" from=".U1 > .pin11" to=".J2 > .pin11" thickness="0.15mm" pcbPathRelativeTo=".TP6 > .pin1"
        pcbPaths={[withViaLandings([".U1 > .pin11", {x: -12.600079, y: -4.2, via: true, toLayer: "bottom"},
          {x: -8.300079, y: -8.5}, {x: 32.599808, y: -8.5},
          {x: 40.35, y: -0.749808, via: true, toLayer: "top"}, ".J2 > .pin11"])]} />
      <trace name="CS_CHANNEL" from=".U1 > .pin12" to=".J2 > .pin12" thickness="0.15mm" pcbPathRelativeTo=".TP6 > .pin1"
        pcbPaths={[withViaLandings([".U1 > .pin12", {x: -12.200029, y: -4.0},
          {x: -11.800029, y: -4.4, via: true, toLayer: "bottom"},
          {x: -8.200029, y: -8}, {x: 32.599936, y: -8},
          {x: 40.35, y: -0.249936, via: true, toLayer: "top"}, ".J2 > .pin12"])]} />
      <trace name="BUSY_CHANNEL" from=".U1 > .pin16" to=".J2 > .pin9" thickness="0.15mm" pcbPathRelativeTo=".TP6 > .pin1"
        pcbPaths={[withViaLandings([".U1 > .pin16", {x: -9.1, y: -2.200148}, {x: -9.1, y: -5.25},
          {x: -5.35, y: -9, via: true, toLayer: "bottom"}, {x: 33.099806, y: -9},
          {x: 40.35, y: -1.749806, via: true, toLayer: "top"}, ".J2 > .pin9"])]} />
      <trace name="SCK_CHANNEL" from=".R14 > .pin2" to=".J2 > .pin13" thickness="0.15mm" pcbPathRelativeTo=".TP6 > .pin1"
        pcbPaths={[withViaLandings([".R14 > .pin2", {x: -10.3, y: -7.246636}, {x: -10.3, y: -12.5},
          {x: 2, y: -12.5}, {x: 2, y: 0.250190, via: true, toLayer: "bottom"}, {x: 20, y: 0.250190},
          {x: 40.35, y: 0.250190, via: true, toLayer: "top"}, ".J2 > .pin13"])]} />

      <TYPE_C_31_M_12 name="J1" standard="usb_c" allowOffBoard schWidth={1.771}
        pcbX={-46} pcbY={0} pcbRotation={270} schX={-7} schY={2} schSectionName="USB" schSheetName={sheetOf("USB")}
        connections={{VBUS1: net("VBUS"), VBUS2: net("VBUS"), GND1: net("GND"), GND2: net("GND"),
          SHELL1: net("GND"), SHELL2: net("GND"), SHELL3: net("GND"), SHELL4: net("GND"),
          CC1: net("CC1"), CC2: net("CC2"), DP1: net("USB_DP"), DP2: net("USB_DP"),
          DM1: net("USB_DM"), DM2: net("USB_DM")}} />
      <A_1206L050_33NR name="F1"
        pcbX={-39} pcbY={13} schX={-3} schY={6} schSectionName="USB" schSheetName={sheetOf("USB")}
        connections={{pin1: net("VBUS"), pin2: net("VSYS")}} />
      <USBLC6_2SC6 name="U2" pcbX={-39} pcbY={0} pcbRotation={90}
        schX={0} schY={1} schSectionName="USB" schSheetName={sheetOf("USB")}
        connections={{pin1: net("USB_DP"), pin6: net("USB_DP"), pin3: net("USB_DM"), pin4: net("USB_DM"),
          pin2: net("GND"), pin5: net("VBUS")}} />

      <AP2112K_3_3TRG1 name="U3" pcbX={-31} pcbY={15} pcbRotation={90}
        schX={5} schY={-3} schSectionName="Power" schSheetName={sheetOf("Power")}
        connections={{pin1: net("VSYS"), pin2: net("GND"), pin3: net("VSYS"), pin5: net("V3V3")}} />
      <AP2112K_3_3TRG1 name="U4" pcbX={23} pcbY={-10} pcbRotation={90}
        schX={-8} schY={-3.5} schSectionName="PanelPower" schSheetName={sheetOf("PanelPower")}
        connections={{pin1: net("VSYS"), pin2: net("GND"), pin3: net("EPD_EN"), pin5: net("EPD_3V3")}} />

      <RP2040 name="U1" pcbX={-14} pcbY={0} pcbRotation={90}
        schX={-1} schY={0} schSectionName="MCU" schSheetName={sheetOf("MCU")} schWidth={2.8} schHeight={6}
        connections={{
          pin1: net("V3V3"), pin10: net("V3V3"), pin22: net("V3V3"), pin33: net("V3V3"),
          pin42: net("V3V3"), pin43: net("V3V3"), pin44: net("V3V3"), pin48: net("V3V3"), pin49: net("V3V3"),
          pin23: net("VCORE"), pin45: net("VCORE"), pin50: net("VCORE"), pin57: net("GND"), pin19: net("GND"),
          pin46: net("USB_DM_MCU"), pin47: net("USB_DP_MCU"), pin20: net("XIN"), pin21: net("XOUT"),
          pin51: net("QSPI_SD3"), pin52: net("QSPI_SCLK"), pin53: net("QSPI_SD0"),
          pin54: net("QSPI_SD2"), pin55: net("QSPI_SD1"), pin56: net("QSPI_SS"),
          pin24: net("SWCLK"), pin25: net("SWDIO"), pin26: net("RUN"),
          pin11: net("EPD_DC"), pin12: net("EPD_CS"), pin13: net("SCK_MCU"), pin14: net("MOSI_MCU"),
          pin15: net("EPD_RST"), pin16: net("EPD_BUSY"), pin17: net("EPD_EN"),
        }} />
      <W25Q16JVSNIQ name="U5" schHeight={0.903} pcbX={-23} pcbY={-7} pcbRotation={90}
        schX={-8} schY={4} schPinArrangement={{leftSide: {pins: [1, 3, 7], direction: "top-to-bottom"}, rightSide: {pins: [5, 2, 6], direction: "top-to-bottom"}, topSide: {pins: [8], direction: "left-to-right"}, bottomSide: {pins: [4], direction: "left-to-right"}}} schSectionName="Flash" schSheetName={sheetOf("Flash")}
        connections={{pin1: net("QSPI_SS"), pin2: net("QSPI_SD1"), pin3: net("QSPI_SD2"), pin4: net("GND"),
          pin5: net("QSPI_SD0"), pin6: net("QSPI_SCLK"), pin7: net("QSPI_SD3"), pin8: net("V3V3")}} />
      <ABM8_272_T3 name="Y1" pcbX={-5.7} pcbY={-2} loadCapacitance="10pF"
        schX={5} schY={5} schSectionName="Clock" schSheetName={sheetOf("Clock")}
        connections={{pin1: net("XIN"), pin3: net("XOSC_OUT"), pin2: net("GND"), pin4: net("GND")}} />
      <TS_1088_AR02016 name="SW1" schRotation={-90} pcbX={-28} pcbY={-19} schX={-8} schY={1} schSectionName="Flash" schSheetName={sheetOf("Flash")}
        connections={{pin1: net("BOOT_N"), pin2: net("GND")}} />
      <TS_1088_AR02016 name="SW2" schRotation={-90} pcbX={-8} pcbY={-19} schX={-6} schY={-4} schSectionName="Control" schSheetName={sheetOf("Control")}
        connections={{pin1: net("RUN"), pin2: net("GND")}} />

      <AFC01_S24FCA_00 name="J2" pcbX={43} pcbY={0} pcbRotation={90}
        schX={8} schY={0} schSectionName="Panel" schSheetName={sheetOf("Panel")} schWidth={2.2} schHeight={2.8}
        connections={{pin2: net("EPD_GDR"), pin3: net("EPD_RESE"), pin5: net("EPD_VSHR"),
          pin8: net("GND"), pin9: net("EPD_BUSY"), pin10: net("EPD_RST"), pin11: net("EPD_DC"),
          pin12: net("EPD_CS"), pin13: net("EPD_SCK"), pin14: net("EPD_MOSI"),
          pin15: net("EPD_3V3"), pin16: net("EPD_3V3"), pin17: net("GND"), pin18: net("EPD_VDD"),
          pin20: net("EPD_VSH"), pin21: net("EPD_VGH"), pin22: net("EPD_VSL"),
          pin23: net("EPD_VGL"), pin24: net("EPD_VCOM"), pin25: net("GND"), pin26: net("GND")}} />
      <SI1308EDL_T1_GE3 name="Q1" pcbX={34} pcbY={-3} pcbRotation={180} schX={-4} schY={3} schSectionName="Boost" schSheetName={sheetOf("Boost")}
        connections={{pin1: net("EPD_GDR"), pin2: net("EPD_RESE"), pin3: net("EPD_SW")}} />
      <FHD252012S_100MT name="L1" pcbX={30} pcbY={-3} schX={-7} schY={5.5} schSectionName="Boost" schSheetName={sheetOf("Boost")}
        connections={{pin1: net("EPD_3V3"), pin2: net("EPD_SW")}} />
      <MBR0530T1G name="D1" schRotation={-90} pcbX={29} pcbY={7} schX={-3} schY={7} schSectionName="Boost" schSheetName={sheetOf("Boost")}
        connections={{pin1: net("EPD_PUMP"), pin2: net("EPD_VGL")}} />
      <MBR0530T1G name="D2" schRotation={-90} pcbX={29} pcbY={4} schX={-6} schY={7} schSectionName="Boost" schSheetName={sheetOf("Boost")}
        connections={{pin1: net("GND"), pin2: net("EPD_PUMP")}} />
      <MBR0530T1G name="D3" schRotation={90} pcbRotation={180} pcbX={35} pcbY={2} schX={-0.5} schY={5.5} schSectionName="Boost" schSheetName={sheetOf("Boost")}
        connections={{pin1: net("EPD_VGH"), pin2: net("EPD_SW")}} />

      {caps.map(([name, capacitance, footprint, sku, rail, pcbX, pcbY, pcbRotation, schSectionName, schX, schY]) => {
        const Part = capacitorParts[sku]
        return <Part key={name} name={name} pcbX={pcbX} pcbY={pcbY} pcbRotation={pcbRotation}
          schX={schX} schY={schY} schSectionName={schSectionName} schSheetName={sheetOf(schSectionName)} schOrientation="vertical"
          connections={{pin1: net(rail), pin2: net("GND")}} />
      })}
      {resistors.map(([name, resistance, footprint, sku, a, b, pcbX, pcbY, pcbRotation, schSectionName, schX, schY]) => {
        const Part = resistorParts[sku]
        return <Part key={name} name={name} pcbX={pcbX} pcbY={pcbY} pcbRotation={pcbRotation}
          schX={schX} schY={schY} schSectionName={schSectionName} schSheetName={sheetOf(schSectionName)}
          schRotation={name === "R15" ? 180 : b === "GND" || a === "V3V3" || a === "EPD_3V3" ? -90 : 0}
          connections={{pin1: net(a), pin2: net(b)}} />
      })}
      {highVoltageCaps.map(([name, capacitance, sku, footprint, a, b, pcbX, pcbY, schSectionName, schX, schY]) => {
        const Part = capacitorParts[sku]
        return <Part key={name} name={name} pcbX={pcbX} pcbY={pcbY} pcbRotation={90}
          schX={schX} schY={schY} schSectionName={schSectionName} schSheetName={sheetOf(schSectionName)} schOrientation={name === "C27" ? "pos_bottom" : "vertical"}
          connections={{pin1: net(a), pin2: net(b)}} />
      })}

      <copperpour name="GND_REFERENCE" layer="bottom" connectsTo="net.GND" clearance={0.25} boardEdgeMargin={0.3} />

      {[[-45,-25],[-45,25],[45,-25],[45,25]].map(([pcbX,pcbY],i) =>
        <Fragment key={i}><hole name={`H${i+1}`} diameter="3.2mm" pcbX={pcbX} pcbY={pcbY} /></Fragment>)}
      {[[-40,24],[40,24],[-40,-24]].map(([pcbX,pcbY],i) =>
        <Fragment key={i}><fiducial name={`FID${i+1}`} pcbX={pcbX} pcbY={pcbY} padDiameter={1} soldermaskPullback={0.5} /></Fragment>)}
      {["GND","V3V3","VCORE","SWDIO","SWCLK","RUN"].map((rail,i) =>
        <testpoint key={rail} name={`TP${i+1}`} padDiameter={1.5} footprintVariant="pad" doNotPlace
          footprint={<footprint>
            <smtpad shape="circle" radius={0.75} portHints={["pin1"]} noSolderPaste solderMaskMargin={0.02} />
            <silkscreentext text="{NAME}" pcbY={1.7} fontSize={1} />
          </footprint>} pcbX={i < 3 ? -17+i*3.5 : 0} pcbY={i < 3 ? -24 : [8,4,0][i-3]}
          schX={i === 5 ? -3.5 : -9+i*2} schY={i === 5 ? -3.33 : -7} schSectionName="Control" schSheetName={sheetOf("Control")} connections={{pin1: net(rail)}} />)}
      <silkscreentext text="USB-C E-PAPER" pcbX={-11} pcbY={23} fontSize={2} />
      <silkscreentext text="RP2040 / 7.5 IN / 800 x 480" pcbX={-8} pcbY={19.5} fontSize={1} />
      <silkscreentext text="REV A / GDEY075T7" pcbX={20} pcbY={-23} fontSize={1} />
      <silkscreentext text="BOOT" pcbX={-28} pcbY={-15.5} fontSize={1} />
      <silkscreentext text="RESET" pcbX={-8} pcbY={-15.5} fontSize={1} />
      <silkscreentext text="RAW EPD / CONTACTS DOWN" pcbX={33} pcbY={-18} fontSize={1} />
      {children}
    </board>
  )
}
