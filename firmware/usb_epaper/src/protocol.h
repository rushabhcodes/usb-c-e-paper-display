#pragma once
#include <stdint.h>
#include <stddef.h>
#include <string.h>

namespace epd {
constexpr uint16_t WIDTH=800, HEIGHT=480, STRIDE=100;
constexpr uint32_t FRAME_SIZE=48000, RX_TIMEOUT_MS=8000;
constexpr uint8_t MAX_PARTIALS=5;
enum Op : uint8_t { INFO=1, IMAGE=2, SLEEP=3 };
enum Mode : uint8_t { AUTO=0, FULL=1, PARTIAL=2, UNCHANGED=3 };
enum Status : uint8_t { OK=0, BAD_REQUEST=1, BAD_CRC=2, RX_TIMEOUT=3, PANEL_FAULT=4 };
inline uint32_t crcStep(uint32_t crc,uint8_t b) {
  crc^=b;
  for(int k=0;k<8;k++) crc=(crc>>1)^((crc&1)?0xedb88320u:0);
  return crc;
}
inline uint32_t crc32(const uint8_t* p,size_t n) {
  uint32_t crc=~0u;
  while(n--) crc=crcStep(crc,*p++);
  return ~crc;
}
inline uint32_t get32(const uint8_t* p) {
  return uint32_t(p[0])|(uint32_t(p[1])<<8)|(uint32_t(p[2])<<16)|(uint32_t(p[3])<<24);
}
inline void put32(uint8_t* p,uint32_t x) {
  for(int i=0;i<4;i++) p[i]=uint8_t(x>>(8*i));
}
inline void header(uint8_t* out,const char* magic,uint8_t op,uint8_t code,
                   uint32_t seq,uint32_t len,uint32_t crc) {
  memcpy(out,magic,4);out[4]=1;out[5]=op;out[6]=code;out[7]=0;
  put32(out+8,seq);put32(out+12,len);put32(out+16,crc);
  put32(out+20,crc32(out,20));
}
struct Request { uint8_t op=0,mode=0;uint32_t seq=0,len=0,crc=0; };
struct Event { bool ready=false; Status status=OK; Request req; };

// Header and payload CRCs are independent. A corrupt length never controls a write.
class Parser {
  uint8_t h[24]{};size_t used=0;uint32_t received=0,crc=~0u,last=0;
  bool payload=false;Request req;uint8_t* target;
 public:
  explicit Parser(uint8_t* buffer):target(buffer){}
  void reset(){used=received=0;payload=false;crc=~0u;}
  Event expire(uint32_t now) {
    if((used||payload)&&uint32_t(now-last)>RX_TIMEOUT_MS) {
      Event e{true,RX_TIMEOUT,req};reset();return e;
    }
    return {};
  }
  Event feed(uint8_t b,uint32_t now) {
    last=now;
    if(payload) {
      target[received++]=b;crc=crcStep(crc,b);
      if(received==req.len) {Event e{true,(~crc==req.crc)?OK:BAD_CRC,req};reset();return e;}
      return {};
    }
    h[used++]=b;
    while(used>=4 && memcmp(h,"EPD1",4)!=0) {memmove(h,h+1,--used);}
    if(used<24) return {};
    if(crc32(h,20)!=get32(h+20)) {memmove(h,h+1,23);used=23;return {};}
    req={h[5],h[6],get32(h+8),get32(h+12),get32(h+16)};
    bool valid=h[4]==1 && h[7]==0 &&
      ((req.op==IMAGE && req.len==FRAME_SIZE && req.mode<=PARTIAL) ||
       ((req.op==INFO||req.op==SLEEP) && req.len==0 && req.crc==0 && req.mode==AUTO));
    if(!valid){Event e{true,BAD_REQUEST,req};reset();return e;}
    if(req.len==0){Event e{true,OK,req};reset();return e;}
    used=0;received=0;crc=~0u;payload=true;return {};
  }
};
struct Rect {uint16_t x=0,y=0,w=0,h=0;};
inline Rect difference(const uint8_t* a,const uint8_t* b) {
  int minx=STRIDE,maxx=-1,miny=HEIGHT,maxy=-1;
  for(int y=0;y<HEIGHT;y++) for(int x=0;x<STRIDE;x++) if(a[y*STRIDE+x]!=b[y*STRIDE+x]) {
    if(x<minx)minx=x;if(x>maxx)maxx=x;if(y<miny)miny=y;if(y>maxy)maxy=y;
  }
  if(maxx<0)return {};
  return {uint16_t(minx*8),uint16_t(miny),uint16_t((maxx-minx+1)*8),uint16_t(maxy-miny+1)};
}
struct Policy {
  bool baseline=false;uint8_t partials=0;
  Mode choose(uint8_t requested,Rect changed) const {
    if(!baseline || requested==FULL)return FULL;
    if(!changed.w)return UNCHANGED;
    if(partials>=MAX_PARTIALS)return FULL;
    return PARTIAL;
  }
  void done(Mode mode){baseline=true;if(mode==FULL)partials=0;else if(mode==PARTIAL)partials++;}
  void invalidate(){baseline=false;partials=0;}
};
}
