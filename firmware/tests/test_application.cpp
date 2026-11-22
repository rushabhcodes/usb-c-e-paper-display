// Compile the actual sketch with hardware boundaries substituted.
#include "fakes/Arduino.h"
#include "fakes/SPI.h"
#include "../usb_epaper/src/protocol.h"
#include <assert.h>
#include <string>
#define _GxEPD2_750_GDEY075T7_H_
struct GxEPD2_750_GDEY075T7 {
  bool busyTimeoutOccurred=false,failNext=false;int full=0,partial=0,initCount=0,previous=0,off=0,sleep=0;
  epd::Rect box;
  GxEPD2_750_GDEY075T7(int,int,int,int){}
  void selectSPI(SPIFake&,SPISettings){}
  void init(int,bool,int,bool){assert(levels[14]==HIGH);assert(SPI1.rx==NOPIN);initCount++;}
  void setBusyCallback(void(*)(const void*),const void*){}
  void writeImageForFullRefresh(const uint8_t*,int,int,int,int){}
  void refresh(bool){full++;if(failNext){busyTimeoutOccurred=true;failNext=false;}}
  void writeImageToPrevious(const uint8_t*,int,int,int,int){previous++;}
  void writeImagePart(const uint8_t*,int,int,int,int,int x,int y,int w,int h){box={uint16_t(x),uint16_t(y),uint16_t(w),uint16_t(h)};}
  void refresh(int,int,int,int){partial++;if(failNext){busyTimeoutOccurred=true;failNext=false;}}
  void powerOff(){off++;}void hibernate(){sleep++;}
};
#include "../usb_epaper/usb_epaper.ino"
uint32_t sequence=1;
uint8_t image[epd::FRAME_SIZE];
int request(uint8_t op,uint8_t mode=0,bool corrupt=false,uint32_t seq=0){
  uint8_t h[24];uint32_t len=op==epd::IMAGE?epd::FRAME_SIZE:0;
  epd::header(h,"EPD1",op,mode,seq?seq:sequence++,len,epd::crc32(image,len));
  Serial.rx.insert(Serial.rx.end(),h,h+24);
  if(len){if(corrupt)image[100]^=1;Serial.rx.insert(Serial.rx.end(),image,image+len);if(corrupt)image[100]^=1;}
  Serial.tx.clear();loop();assert(Serial.tx.size()>24);assert(!memcmp(Serial.tx.data(),"EPA1",4));
  assert(epd::crc32(Serial.tx.data(),20)==epd::get32(Serial.tx.data()+20));
  assert(epd::crc32(Serial.tx.data()+24,Serial.tx.size()-24)==epd::get32(Serial.tx.data()+16));
  return Serial.tx[6];
}
int main(){
  levels[13]=HIGH;setup();assert(levels[14]==LOW&&!powered&&panel.initCount==0);
  assert(request(epd::INFO)==0&&!powered);
  memset(image,0xff,sizeof(image));assert(request(epd::IMAGE,0,true)==epd::BAD_CRC);
  assert(!powered&&panel.full==0);
  assert(request(epd::IMAGE,epd::PARTIAL)==0);assert(panel.full==1&&panel.previous==1&&policy.baseline);
  assert(powered&&levels[14]==HIGH&&SPI1.sck==10&&SPI1.tx==11&&SPI1.rx==NOPIN);
  image[100*10+1]=0;assert(request(epd::IMAGE)==0);assert(panel.partial==1);
  assert(panel.box.x==8&&panel.box.y==10&&panel.box.w==8&&panel.box.h==1);
  int calls=panel.partial+panel.full;assert(request(epd::IMAGE)==0);assert(panel.partial+panel.full==calls);
  for(int i=0;i<4;i++){image[200+i]^=1;assert(request(epd::IMAGE)==0);}
  assert(policy.partials==5);image[300]^=1;request(epd::IMAGE);assert(panel.full==2&&policy.partials==0);
  request(epd::SLEEP);assert(!powered&&!policy.baseline&&panel.sleep==1&&levels[14]==LOW);
  request(epd::IMAGE,epd::PARTIAL);assert(panel.full==3&&panel.initCount==2);
  panel.failNext=true;image[400]^=1;uint32_t retry=sequence++;
  assert(request(epd::IMAGE,0,false,retry)==epd::PANEL_FAULT);assert(!powered&&!policy.baseline);
  calls=panel.partial+panel.full;
  assert(request(epd::IMAGE,0,false,retry)==epd::PANEL_FAULT);assert(panel.partial+panel.full==calls);
  assert(request(epd::IMAGE)==0&&powered&&panel.full==4);
  puts("PASS: actual sketch USB framing, power sequence, baseline, partial bounds, cleanup, sleep, BUSY fault and ACK replay");
}
