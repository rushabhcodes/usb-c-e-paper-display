#pragma once
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>
#include <vector>
#include <deque>
#include <initializer_list>
#define LOW 0
#define HIGH 1
#define OUTPUT 1
#define INPUT 0
inline int levels[32]{};
inline uint32_t clockMs=0;
inline void pinMode(int,int){}
inline void digitalWrite(int pin,int value){levels[pin]=value;}
inline int digitalRead(int pin){return levels[pin];}
inline void delay(int n){clockMs+=n;}
inline uint32_t millis(){return clockMs;}
struct SerialFake {
  std::deque<uint8_t> rx;std::vector<uint8_t> tx;
  void begin(int){}void flush(){}
  int available(){return rx.size();}
  int read(){int b=rx.front();rx.pop_front();return b;}
  size_t write(const uint8_t* b,size_t n){tx.insert(tx.end(),b,b+n);return n;}
};
inline SerialFake Serial;
