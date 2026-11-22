#pragma once
#define NOPIN 255
#define MSBFIRST 1
#define SPI_MODE0 0
struct SPISettings{SPISettings(int,int,int){}};
struct SPIFake {
  int rx=12,sck=-1,tx=-1;bool active=false;
  void setRX(int p){rx=p;}void setSCK(int p){sck=p;}void setTX(int p){tx=p;}
  void begin(){active=true;}void end(){active=false;}
};
inline SPIFake SPI1;
