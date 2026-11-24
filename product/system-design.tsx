import { systemblock } from "@tscircuit/core"

export function SystemDesign() {
  return <>
    <systemblock.page name="IMAGE_PIPELINE" displayName="USB image and refresh pipeline" direction="right"
      description="USB CDC transfers CRC-checked 800 x 480 monochrome images. RP2354B keeps a previous frame, updates the changed rectangle and periodically performs a clean full refresh.">
      <systemblock.component name="HOST" displayName="Computer / image sender" description="Python epaper.py converts images and sends framed, CRC-checked commands." />
      <systemblock.component name="USB" displayName="USB-C data interface" pcbComponentNames={["J1","U2","R3","R4"]} description="USB 2.0 Full Speed device; CC pull-downs, ESD protection and data series resistors." />
      <systemblock.component name="MCU" displayName="RP2354B / USB CDC" pcbComponentName="U1" description="Two 48,000-byte frames; bounds and CRC checks; changed-region calculation; BUSY timeout and power sequencing." />
      <systemblock.component name="FLASH" displayName="2 MB internal flash" pcbComponentName="U1" description="Firmware storage and RP2354B ROM BOOTSEL programming." />
      <systemblock.component name="CLOCK" displayName="12 MHz reference" pcbComponentNames={["Y1","R7","C20","C21"]} />
      <systemblock.component name="SPI" displayName="SPI1 / raw-panel connector" pcbComponentNames={["J2","R14","R15","R12","R13"]} description="GP10 SCK, GP11 MOSI, GP9 CS, GP8 DC, GP12 RESET and GP13 BUSY." />
      <systemblock.component name="EPAPER_DISPLAY" displayName="GDEY075T7 / UC8179" description="7.5-inch raw 800 x 480 monochrome panel. Partial updates follow a full baseline; clean full refresh after five partial updates." />
      <systemblock.component name="SERVICE" displayName="BOOTSEL / reset / SWD" pcbComponentNames={["SW1","SW2","TP4","TP5","TP6"]} />
      <systemblock.connection from="HOST" to="USB" label="USB-C cable" direction="both" />
      <systemblock.connection from="USB" to="MCU" label="12 Mbit/s USB CDC" direction="both" />
      <systemblock.connection from="MCU" to="FLASH" label="Stacked flash die" direction="both" />
      <systemblock.connection from="CLOCK" to="MCU" label="12 MHz" />
      <systemblock.connection from="SERVICE" to="MCU" label="ROM / reset / debug" direction="both" />
      <systemblock.connection from="MCU" to="SPI" label="SPI1 + control / BUSY" direction="both" />
      <systemblock.connection from="SPI" to="EPAPER_DISPLAY" label="24-contact FPC" direction="both" />
    </systemblock.page>
    <systemblock.page name="POWER_TREE" displayName="USB and onboard panel power" direction="right"
      description="USB 5 V feeds independent MCU and switched-panel regulators. All high-voltage panel boost and reservoir components are on the controller PCB; no external display driver board is needed.">
      <systemblock.component name="USB_5V" displayName="USB-C / 5 V" pcbComponentNames={["J1","R1","R2"]} />
      <systemblock.component name="FUSE" displayName="500 mA resettable fuse" pcbComponentName="F1" />
      <systemblock.component name="MCU_REG" displayName="MCU 3.3 V regulator" pcbComponentNames={["U3","C3","C4"]} />
      <systemblock.component name="RP2354B" displayName="RP2354B / internal flash" pcbComponentNames={["U1"]} description="External 1.092 V buck supply; internal regulator disabled per Raspberry Pi Figure 24. Local bypass on every supply pin." />
      <systemblock.component name="CORE_REG" displayName="1.092 V core buck" pcbComponentNames={["U5","L2","C34","C35","C36","R16","R17"]} description="TLV62569: 2.2 uH and 2 x 22 uF; 8.2 k / 10 k feedback; enabled from V3V3." />
      <systemblock.component name="PANEL_REG" displayName="Switched panel 3.3 V" pcbComponentNames={["U4","R9","C5","C6","C26"]} description="GP14 enables U4. R9 holds the panel supply off during reset." />
      <systemblock.component name="BOOST" displayName="Onboard panel boost / pump" pcbComponentNames={["Q1","L1","D1","D2","D3","R10","R11","C27"]} />
      <systemblock.component name="RESERVOIRS" displayName="50 V panel rail capacitors" pcbComponentNames={["C22","C24","C25","C28","C29","C30","C31"]} />
      <systemblock.component name="RAW_PANEL" displayName="Raw display power rails" pcbComponentName="J2" />
      <systemblock.connection from="USB_5V" to="FUSE" label="VBUS" kind="power" />
      <systemblock.connection from="FUSE" to="MCU_REG" label="VSYS" kind="power" />
      <systemblock.connection from="FUSE" to="CORE_REG" label="VSYS" kind="power" />
      <systemblock.connection from="MCU_REG" to="CORE_REG" label="Enable" />
      <systemblock.connection from="CORE_REG" to="RP2354B" label="VCORE / 1.092 V" kind="power" />
      <systemblock.connection from="FUSE" to="PANEL_REG" label="VSYS" kind="power" />
      <systemblock.connection from="MCU_REG" to="RP2354B" label="V3V3" kind="power" />
      <systemblock.connection from="RP2354B" to="PANEL_REG" label="GP14 enable" />
      <systemblock.connection from="PANEL_REG" to="BOOST" label="EPD_3V3" kind="power" />
      <systemblock.connection from="PANEL_REG" to="RAW_PANEL" label="3.3 V logic" kind="power" />
      <systemblock.connection from="BOOST" to="RESERVOIRS" label="UC8179-controlled rails" kind="power" />
      <systemblock.connection from="RESERVOIRS" to="RAW_PANEL" label="VGH / VGL / VSH / VSL / VCOM" kind="power" />
    </systemblock.page>
  </>
}
