#include <Wire.h>
#include <FastLED.h>

#define SENSOR_PIN 36

#define LED_PIN     14
#define NUM_LEDS    25

#define ADC_MAX 4095
 
 const int sampleWindow = 50;                              // Sample window width in mS (50 mS = 20Hz)
 unsigned int sample;
 
 CRGB leds[NUM_LEDS];
 
 void setup ()
 {
  FastLED.addLeds<WS2812, LED_PIN, GRB>(leds, NUM_LEDS);
  Serial.begin(9600);
  pinMode(SENSOR_PIN,INPUT);
 
 }
 
 int filter(float data){
   static float avg = 0;
   float alpha = 0.1;
 
   avg = ((alpha * data) + ((1. - alpha) * avg));
   
   return (int)avg;
 }
 
 void loop ()
 {
    unsigned long startMillis= millis();                   // Start of sample window
    float peakToPeak = 0;                                  // peak-to-peak level
 
    unsigned int signalMax = 0;                            //minimum value
    unsigned int signalMin = ADC_MAX;                         //maximum value
 
                                                           // collect data for 50 mS
    while (millis() - startMillis < sampleWindow)
    {
       sample = analogRead(SENSOR_PIN);                    //get reading from microphone
       if (sample < ADC_MAX)                                  // toss out spurious readings
       {
          if (sample > signalMax)
          {
             signalMax = sample;                           // save just the max levels
          }
          else if (sample < signalMin)
          {
             signalMin = sample;                           // save just the min levels
          }
       }
    }
 
    peakToPeak = signalMax - signalMin;                    // max - min = peak-peak amplitude
    int db = map(peakToPeak,20,900,49.5,90);             //calibrate for deciBels
    db = filter((float)db);
     Serial.println(db);
 
   if (db <= 50)
   {
 
    for(int i=0; i<NUM_LEDS; i++){  //TURN LED GREEN
      leds[i] = CRGB(0, 255, 0);
      FastLED.show();
   }
    }
   else if (db > 50 && db<55)
   {
 
     for(int i=0; i<NUM_LEDS; i++){ //TURN LED YELLOW
      leds[i] = CRGB(255, 255, 0);
      FastLED.show();
   }
    }
   else if (db>=55)
   {
 
    for(int i=0; i<NUM_LEDS; i++){  //TURN LED RED
      leds[i] = CRGB(255, 0, 0);
      FastLED.show();
 
   }
   
    
  }
 }
