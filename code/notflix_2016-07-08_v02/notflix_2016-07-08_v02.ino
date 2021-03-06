// notflix_2016-06-10_v01
//
// From the "fake-tv-light-for-engineers" project and sketch by Adafruit's Phillip Burgess, 2016-05-12
//
//   modified 2016-06-10 and 2016-07-08 by Cedar Grove Maker Studios
//   added initial and exit scrolling title, two-hour timer, and analog brightness control (Analog Input A3)
//
//   Sketch uses 31,572 bytes (97%) of program storage space. Maximum is 32,256 bytes.
//   Global variables use 102 bytes (4%) of dynamic memory, leaving 1,946 bytes for local variables. Maximum is 2,048 bytes.
//

#include <Adafruit_NeoPixel.h>
#include "data.h" // Output of Python script
 
#define NUM_LEDS 40
#define PIN       6
Adafruit_NeoPixel strip = Adafruit_NeoPixel(NUM_LEDS, PIN, NEO_GRB);
 
#define  numPixels (sizeof(colors) / sizeof(colors[0]))
uint32_t pixelNum;
uint16_t pr = 0, pg = 0, pb = 0; // Prev R, G, B
uint8_t notflix [47] = {0,0,0,0,0,0,0,0,31,2,4,31,0,14,17,14,0,1,31,1,0,31,5,1,0,31,16,16,0,17,31,17,0,17,10,4,10,17,0,0,0,0,0,0,0,0,0};
 
void setup() {
  uint16_t i, j ;
  
  strip.begin();
  randomSeed(analogRead(A0));
  pixelNum = random(numPixels); // Begin at random point

  disp_notflix();

}
 
void loop() {
  uint32_t totalTime, fadeTime, holdTime, startTime, elapsed;
  uint16_t nr, ng, nb, r, g, b, i, j;
  uint8_t  hi, lo, r8, g8, b8, frac;
  
  strip.setBrightness(map(analogRead(A3),0,1023,11,255));    // set brightness from potentiometer
  
  // Read next 16-bit (5/6/5) color
  hi = pgm_read_byte(&colors[pixelNum * 2    ]);
  lo = pgm_read_byte(&colors[pixelNum * 2 + 1]);
  if(++pixelNum >= numPixels) pixelNum = 0;
 
  // Expand to 24-bit (8/8/8)
  r8 = (hi & 0xF8) | (hi >> 5);
  g8 = (hi << 5) | ((lo & 0xE0) >> 3) | ((hi & 0x06) >> 1);
  b8 = (lo << 3) | ((lo & 0x1F) >> 2);
  // Apply gamma correction, further expand to 16/16/16
  nr = (uint8_t)pgm_read_byte(&gamma8[r8]) * 257; // New R/G/B
  ng = (uint8_t)pgm_read_byte(&gamma8[g8]) * 257;
  nb = (uint8_t)pgm_read_byte(&gamma8[b8]) * 257;
 
  totalTime = random(250, 2500);    // Semi-random pixel-to-pixel time
  fadeTime  = random(0, totalTime); // Pixel-to-pixel transition time
  if(random(10) < 3) fadeTime = 0;  // Force scene cut 30% of time
  holdTime  = totalTime - fadeTime; // Non-transition time
 
  startTime = millis();
  for(;;) {
    elapsed = millis() - startTime;
    if(elapsed >= fadeTime) elapsed = fadeTime;
    if(fadeTime) {
      r = map(elapsed, 0, fadeTime, pr, nr); // 16-bit interp
      g = map(elapsed, 0, fadeTime, pg, ng);
      b = map(elapsed, 0, fadeTime, pb, nb);
    } else { // Avoid divide-by-zero in map()
      r = nr;
      g = ng;
      b = nb;
    }
    for(i=0; i<NUM_LEDS; i++) {
      r8   = r >> 8; // Quantize to 8-bit
      g8   = g >> 8;
      b8   = b >> 8;
      frac = (i << 8) / NUM_LEDS; // LED index scaled to 0-255
      if((r8 < 255) && ((r & 0xFF) >= frac)) r8++; // Boost some fraction
      if((g8 < 255) && ((g & 0xFF) >= frac)) g8++; // of LEDs to handle
      if((b8 < 255) && ((b & 0xFF) >= frac)) b8++; // interp > 8bit
      strip.setPixelColor(i, r8, g8, b8);
    }
    strip.show();
    if(elapsed >= fadeTime) break;
  }
  delay(holdTime);
 
  pr = nr; // Prev RGB = new RGB
  pg = ng;
  pb = nb;

  // darken display after two hours (7200000ms) and wait for reset
  if(millis() > 7200000) {
    while (true) {
      strip.setBrightness(255);    // re-set brightness to initial default
      disp_notflix();
    }
  }
}

// display NOTFLIX graphic on startup screen
void disp_notflix() {

  for (int i=0; i<NUM_LEDS; i++) {  // wipe screen to dark
    strip.setPixelColor(i,0,0,0);
    strip.show();
    delay(50);
  }

  for (int i=1; i<47-8; i++) {
    for (int j=0; j<8; j++)  {
      
      // display rolling graphic
      if (notflix[i+j]& 1) strip.setPixelColor(j   ,0,8,0);
      else                 strip.setPixelColor(j   ,0,0,0);
      
      if (notflix[i+j]& 2) strip.setPixelColor(j+ 8,0,8,0);
      else                 strip.setPixelColor(j+ 8,0,0,0);
      
      if (notflix[i+j]& 4) strip.setPixelColor(j+16,0,8,0);
      else                 strip.setPixelColor(j+16,0,0,0);
      
      if (notflix[i+j]& 8) strip.setPixelColor(j+24,0,8,0);
      else                 strip.setPixelColor(j+24,0,0,0);
      
      if (notflix[i+j]&16) strip.setPixelColor(j+32,0,8,0);
      else                 strip.setPixelColor(j+32,0,0,0);
    }
    strip.show();
    delay(300);
  }
}

