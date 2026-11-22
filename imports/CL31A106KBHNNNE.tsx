import type { CapacitorProps } from "@tscircuit/props"

export const CL31A106KBHNNNE = (props: Omit<CapacitorProps, "capacitance">) => {
  const { name = "C1", ...restProps } = props

  return (
    <capacitor
      maxVoltageRating="50V"
      name={name}
      capacitance="10uF"
      supplierPartNumbers={{
  "jlcpcb": [
    "C13585"
  ]
}}
      manufacturerPartNumber="CL31A106KBHNNNE"
      footprint={<footprint>
        <smtpad solderMaskMargin="0.02mm" solderPasteMargin="0mm" portHints={["pin2"]} pcbX="1.59258mm" pcbY="0mm" width="1.485011mm" height="1.7279874mm" shape="rect" />
<smtpad solderMaskMargin="0.02mm" solderPasteMargin="0mm" portHints={["pin1"]} pcbX="-1.59258mm" pcbY="0mm" width="1.485011mm" height="1.7279874mm" shape="rect" />
<silkscreentext text="{NAME}" pcbX="0mm" pcbY="0mm" pcbRotation={360} layer="bottom" anchorAlignment="center" fontSize="1mm" />
<courtyardoutline outline={[{"x":-2.585085499999991,"y":1.1139937000000373},{"x":2.5850854999998774,"y":1.1139937000000373},{"x":2.5850854999998774,"y":-1.1139937000000373},{"x":-2.585085499999991,"y":-1.1139937000000373},{"x":-2.585085499999991,"y":1.1139937000000373}]} />
      </footprint>}
      cadModel={{
        objUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C13585.obj?uuid=c6790e9475e1483991d2c64340b24e96",
        stepUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C13585.step?uuid=c6790e9475e1483991d2c64340b24e96",
        pcbRotationOffset: 0,
        modelOriginPosition: { x: 0, y: 0, z: -0.65 },
      }}
      {...restProps}
    />
  )
}