#define USB_CFG_DEVICE_NAME     'D','i','g','i','L','e','d'
#define USB_CFG_DEVICE_NAME_LEN 7
#include <DigiUSB.h>


#include "Adafruit_NeoPixel.h"



#define PIXEL_DATA_PIN 0
#define LED_PIN 1

Adafruit_NeoPixel_LJE pixels(1, PIXEL_DATA_PIN, NEO_GRB + NEO_KHZ800);


void setup() {
  // put your setup code here, to run once:
  pixels.begin();
  pinMode(LED_PIN, OUTPUT);
  DigiUSB.begin();
  digitalWrite(LED_PIN, 0);
}

bool blink = true;
const int rgb_values_count = 3;
const byte start_value = 115;
byte rgb_values[rgb_values_count];
byte next_value = 0;
bool got_start = false;


void loop() {
  DigiUSB.refresh();
  if (DigiUSB.available() > 0)
  {
    byte in = DigiUSB.read();
    if (got_start)
    {
      rgb_values[next_value] = in;
      ++next_value;
      if (next_value >= rgb_values_count)
      {
        pixels.setPixelColor(0, rgb_values[0],rgb_values[1],rgb_values[2]);
        pixels.show(); // This sends the updated pixel color to the hardware.
        digitalWrite(LED_PIN, 0);
        got_start = false;
      }
    } 
    else if (in == start_value)
    {
      got_start = true;
      next_value = 0;
      digitalWrite(LED_PIN, 1);
    }
  }
}
