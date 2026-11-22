#include "../usb_epaper/src/protocol.h"
#include <assert.h>
#include <stdio.h>
#include <vector>
using namespace epd;
uint8_t a[FRAME_SIZE],b[FRAME_SIZE],rx[FRAME_SIZE];
Event send(Parser& p,std::vector<uint8_t>& bytes,uint32_t t=100){
  Event result;for(auto c:bytes){Event e=p.feed(c,t);if(e.ready)result=e;}return result;
}
std::vector<uint8_t> make(uint8_t op,uint8_t mode,uint32_t seq,const uint8_t* data,size_t size){
  std::vector<uint8_t> out(24+size);header(out.data(),"EPD1",op,mode,seq,size,crc32(data,size));
  if(size)memcpy(out.data()+24,data,size);return out;
}
int main(){
  assert(crc32((const uint8_t*)"123456789",9)==0xcbf43926);
  Parser parser(rx);auto image=make(IMAGE,AUTO,42,a,FRAME_SIZE);
  // Payload may contain header magic without breaking framing.
  memcpy(a+100,"EPD1",4);image=make(IMAGE,AUTO,42,a,FRAME_SIZE);
  auto e=send(parser,image);assert(e.ready&&e.status==OK&&e.req.seq==42&&!memcmp(rx,a,FRAME_SIZE));
  image[88]^=1;e=send(parser,image);assert(e.ready&&e.status==BAD_CRC);
  // Corrupted header and junk must resynchronize to the following valid packet.
  auto info=make(INFO,AUTO,43,nullptr,0);auto bad=info;bad[12]^=0xff;
  send(parser,bad);e=send(parser,info);assert(e.ready&&e.status==OK&&e.req.seq==43);
  auto invalid=make(IMAGE,AUTO,44,a,8);e=send(parser,invalid);assert(e.ready&&e.status==BAD_REQUEST);
  parser.reset();image=make(IMAGE,PARTIAL,45,a,FRAME_SIZE);
  for(int i=0;i<40;i++)assert(!parser.feed(image[i],100).ready);
  e=parser.expire(8101);assert(e.ready&&e.status==RX_TIMEOUT);
  e=send(parser,info,8200);assert(e.ready&&e.status==OK);
  assert(difference(b,b).w==0);a[0]=0;memset(a,0,FRAME_SIZE);memset(b,0,FRAME_SIZE);
  b[100*17+3]=128;b[100*23+8]=1;
  auto r=difference(a,b);assert(r.x==24&&r.y==17&&r.w==48&&r.h==7);
  Policy p;assert(p.choose(PARTIAL,r)==FULL);p.done(FULL);
  for(int i=0;i<5;i++){assert(p.choose(AUTO,r)==PARTIAL);p.done(PARTIAL);}
  assert(p.choose(PARTIAL,r)==FULL);assert(p.choose(AUTO,{})==UNCHANGED);
  assert(p.choose(FULL,{})==FULL);p.done(FULL);assert(p.partials==0);
  p.invalidate();assert(p.choose(AUTO,{})==FULL);
  puts("PASS: CRC, stream resync, bounds, transfer timeout, difference bounds, baseline and cleanup policy");
}
