import {expect,test} from "bun:test"
import {RootCircuit} from "@tscircuit/core"
import {checkEachPcbTraceNonOverlapping} from "@tscircuit/checks"
import type {AnyCircuitElement} from "circuit-json"

test("autorouted inner-layer branches retain their declared net at native vias",async()=>{
  const circuit=new RootCircuit({platform:{useCloudAutorouter:false,autorouterThreads:1}})
  circuit.add(<board width={16} height={10} layers={4} minTraceWidth={0.15}
    autorouter={{local:true,preset:"tscircuit",serverCacheEnabled:false}}>
    <net name="GND" isGroundNet />
    <testpoint name="TP1" footprintVariant="pad" doNotPlace pcbX={-5} connections={{pin1:"net.GND"}} />
    <testpoint name="TP2" footprintVariant="pad" doNotPlace pcbX={5} connections={{pin1:"net.GND"}} />
    <via name="V1" pcbX={-3} fromLayer="top" toLayer="bottom" holeDiameter={0.3} outerDiameter={0.55} connectsTo="net.GND" />
    <via name="V2" pcbX={3} fromLayer="top" toLayer="bottom" holeDiameter={0.3} outerDiameter={0.55} connectsTo="net.GND" />
    <trace name="LEFT_STUB" from=".TP1 > .pin1" to=".V1 > .top" thickness={0.15} pcbPath={[{x:1,y:0}]} />
    <trace name="RIGHT_STUB" from=".TP2 > .pin1" to=".V2 > .top" thickness={0.15} pcbPath={[{x:-1,y:0}]} />
    <keepout shape="rect" layer="top" pcbX={0} pcbY={0} width={4} height={12} />
  </board>)
  await circuit.renderUntilSettled()
  const data=circuit.getCircuitJson() as (AnyCircuitElement & {connection_name?:string})[]
  const net=data.filter(e=>e.type==="source_net").find(e=>e.name==="GND")!
  const routed=data.filter(e=>e.type==="pcb_trace").filter(e=>e.connection_name===net.source_net_id)
  expect(routed.length).toBeGreaterThan(0)
  expect(routed.some(t=>t.type==="pcb_trace"&&t.route.some(p=>p.route_type==="wire"&&p.layer!=="top"))).toBe(true)
  for(const trace of routed){
    const source=data.find(e=>e.type==="source_trace"&&trace.type==="pcb_trace"&&e.source_trace_id===trace.source_trace_id)
    expect(source?.type==="source_trace"&&source.connected_source_net_ids).toContain(net.source_net_id)
    expect(source?.type==="source_trace"?source.min_trace_thickness:null).toBeUndefined()
  }
  expect(data.filter(e=>e.type.endsWith("_error"))).toEqual([])
  // Correct net attribution must still expose a real foreign-net copper short.
  const foreignCopper:AnyCircuitElement[]=[
    {type:"source_net",source_net_id:"source_net_999",name:"FOREIGN",member_source_group_ids:[]},
    {type:"pcb_via",pcb_via_id:"pcb_via_foreign",x:0,y:0,hole_diameter:0.3,outer_diameter:0.55,
      layers:["top","inner1","inner2","bottom"],source_net_id:"source_net_999"},
  ]
  expect(checkEachPcbTraceNonOverlapping([...data,...foreignCopper]).length).toBeGreaterThan(0)
},120_000)

test("explicit full-stack via layers expose native inner-layer trace endpoints",async()=>{
  const circuit=new RootCircuit({platform:{useCloudAutorouter:false,autorouterThreads:1}})
  circuit.add(<board width={16} height={10} layers={4} allowBlindAndBuriedVias={false}
    autorouter={{local:true,preset:"tscircuit",serverCacheEnabled:false}}>
    <net name="GND" isGroundNet />
    <testpoint name="TP1" footprintVariant="pad" doNotPlace pcbX={-5} connections={{pin1:"net.GND"}} />
    <testpoint name="TP2" footprintVariant="pad" doNotPlace pcbX={5} connections={{pin1:"net.GND"}} />
    <via name="V1" pcbX={-3} layers={["top","inner1","inner2","bottom"]} holeDiameter={0.3} outerDiameter={0.55} connectsTo="net.GND" />
    <via name="V2" pcbX={3} layers={["top","inner1","inner2","bottom"]} holeDiameter={0.3} outerDiameter={0.55} connectsTo="net.GND" />
    <trace from=".TP1 > .pin1" to=".V1 > .top" pcbPath={[{x:1,y:0}]} />
    <trace from=".TP2 > .pin1" to=".V2 > .top" pcbPath={[{x:-1,y:0}]} />
    <trace from=".V1 > .inner2" to=".V2 > .inner2" pcbPath={[{x:1,y:0}]} />
  </board>)
  await circuit.renderUntilSettled()
  const data=circuit.getCircuitJson()
  expect(data.filter(e=>e.type.endsWith("_error"))).toEqual([])
  expect(data.filter(e=>e.type==="source_port"&&e.name==="inner2")).toHaveLength(2)
  expect(data.filter(e=>e.type==="pcb_via").every(v=>v.layers.join(",")==="top,inner1,inner2,bottom")).toBe(true)
  expect(data.some(e=>e.type==="pcb_trace"&&e.route.some(p=>p.route_type==="wire"&&p.layer==="inner2"))).toBe(true)
},120_000)
