// SPDX-License-Identifier: GPL-3.0-or-later
// USB-C raw GDEY075T7 controller, PCB Rev C / RP2354B. See ../README.md.
#include <Arduino.h>
#include <SPI.h>
#if defined(ARDUINO_ARCH_RP2040) && (!defined(PICO_RP2350) || !PICO_RP2350)
#error "PCB Rev C requires the RP2350B target; RP2040 UF2 files are incompatible"
#endif
#include "src/protocol.h"
#include "src/vendor/gdey/GxEPD2_750_GDEY075T7.h"

constexpr uint8_t CS=9,DC=8,RST=12,BUSY=13,EN=14,PANEL_SCK=10,PANEL_MOSI=11;
GxEPD2_750_GDEY075T7 panel(CS,DC,RST,BUSY);
uint8_t currentFrame[epd::FRAME_SIZE],incomingFrame[epd::FRAME_SIZE];
epd::Parser parser(incomingFrame);
epd::Policy policy;
bool powered=false;
// Stop-and-wait replay: lost ACK can be retried without another panel refresh.
bool cached=false;
epd::Request lastRequest;
uint8_t lastStatus=0;
char lastJson[384];

void sendReply(const epd::Request& r,uint8_t status,const char* json) {
  uint8_t h[24];size_t n=strlen(json);
  epd::header(h,"EPA1",r.op|0x80,status,r.seq,n,epd::crc32((const uint8_t*)json,n));
  Serial.write(h,sizeof(h));Serial.write((const uint8_t*)json,n);Serial.flush();
}
void powerCut() {
  SPI1.end();
  // Drive all panel inputs low BEFORE removing 3.3 V to avoid back-powering.
  for(uint8_t p:{CS,DC,RST,PANEL_SCK,PANEL_MOSI}) {digitalWrite(p,LOW);pinMode(p,OUTPUT);}
  pinMode(BUSY,INPUT);
  digitalWrite(EN,LOW);powered=false;policy.invalidate();
}
void busyYield(const void*){delay(1);}
void powerUp() {
  digitalWrite(EN,HIGH);delay(20);
  SPI1.setRX(NOPIN); // GP12 is RESET; never claim it as the SPI1 MISO pin.
  SPI1.setSCK(PANEL_SCK);SPI1.setTX(PANEL_MOSI);SPI1.begin();
  panel.selectSPI(SPI1,SPISettings(4000000,MSBFIRST,SPI_MODE0));
  panel.init(0,true,10,false);panel.setBusyCallback(busyYield,nullptr);
  powered=true;
}
bool displayImage(epd::Mode mode,epd::Rect r) {
  panel.busyTimeoutOccurred=false;
  if(!powered)powerUp();
  if(mode==epd::FULL) {
    panel.writeImageForFullRefresh(incomingFrame,0,0,800,480);
    panel.refresh(false);
    // Explicitly seed both banks after the clean full waveform.
    panel.writeImageToPrevious(incomingFrame,0,0,800,480);
  } else {
    panel.writeImagePart(incomingFrame,r.x,r.y,800,480,r.x,r.y,r.w,r.h);
    panel.refresh(r.x,r.y,r.w,r.h);
    // N2OCP in the UC8179 copies the new bank to previous after refresh.
  }
  panel.powerOff(); // HV off, logic supply stays on to preserve previous-image RAM.
  if(panel.busyTimeoutOccurred || digitalRead(BUSY)==LOW) {powerCut();return false;}
  memcpy(currentFrame,incomingFrame,epd::FRAME_SIZE);policy.done(mode);return true;
}
void handle(epd::Event e) {
  if(!e.ready)return;
  if(e.status!=epd::OK) {sendReply(e.req,e.status,"{\"error\":\"invalid or incomplete transfer\"}");return;}
  auto r=e.req;
  if(cached && r.seq==lastRequest.seq && r.op==lastRequest.op && r.mode==lastRequest.mode &&
     r.len==lastRequest.len && r.crc==lastRequest.crc) {sendReply(r,lastStatus,lastJson);return;}
  uint32_t start=millis();epd::Mode actual=epd::UNCHANGED;epd::Rect box{};
  uint8_t status=epd::OK;
  if(r.op==epd::IMAGE) {
    box=epd::difference(currentFrame,incomingFrame);actual=policy.choose(r.mode,box);
    if(actual==epd::FULL)box={0,0,800,480};
    if(actual!=epd::UNCHANGED && !displayImage(actual,box))status=epd::PANEL_FAULT;
  } else if(r.op==epd::SLEEP) {
    if(powered) {panel.busyTimeoutOccurred=false;panel.hibernate();if(panel.busyTimeoutOccurred)status=epd::PANEL_FAULT;}
    powerCut();
  }
  const char* name=actual==epd::FULL?"full":actual==epd::PARTIAL?"partial":"unchanged";
  snprintf(lastJson,sizeof(lastJson),
    "{\"device\":\"usb-epaper-revc-rp2354b\",\"firmware\":\"1.1.0\",\"panel\":\"GDEY075T7\","
    "\"width\":800,\"height\":480,\"baseline\":%s,\"powered\":%s,\"partials\":%u,"
    "\"max_partials\":5,\"mode\":\"%s\",\"bbox\":[%u,%u,%u,%u],\"elapsed_ms\":%lu}",
    policy.baseline?"true":"false",powered?"true":"false",policy.partials,name,
    box.x,box.y,box.w,box.h,(unsigned long)(millis()-start));
  lastRequest=r;lastStatus=status;cached=true;sendReply(r,status,lastJson);
}
void setup() {
  digitalWrite(EN,LOW);pinMode(EN,OUTPUT);powerCut();
  memset(currentFrame,0xff,sizeof(currentFrame));
  Serial.begin(115200); // USB CDC: baud rate does not determine USB transfer speed.
}
void loop() {
  handle(parser.expire(millis()));
  while(Serial.available())handle(parser.feed(uint8_t(Serial.read()),millis()));
  delay(1);
}
