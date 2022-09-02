


#include <FastLED.h>

#include <Wire.h>

#include <WiFi.h>
#include <HTTPClient.h>
#define SENSOR_PIN 36

#define LED_PIN     14
#define NUM_LEDS    25

#define ADC_MAX 4095



//Your Domain name with URL path or IP address with path
const char* serverName = "http://b713-212-175-35-11.eu.ngrok.io/sensor";

// the following variables are unsigned longs because the time, measured in
// milliseconds, will quickly become a bigger number than can be stored in an int.
unsigned long lastTime = 0;

// Set timer to 2 seconds (5000)
unsigned long timerDelay = 1000;
 const int sampleWindow = 50;                              // Sample window width in mS (50 mS = 20Hz)
 unsigned int sample;
 const char* ssid = "INNOVATION";
 const char* password = "Technology2019!!";

 
 CRGB leds[NUM_LEDS];

      


 void setup ()
 {
  FastLED.addLeds<WS2812, LED_PIN, GRB>(leds, NUM_LEDS);
  Serial.begin(9600);
  pinMode(SENSOR_PIN,INPUT);

  //connect to WiFi network
 
    WiFi.begin(ssid, password);
  Serial.println("Connecting");
  while(WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print("connecting...");
    delay(1000);
  }
  Serial.println("");
  Serial.print("Connected to WiFi network with IP Address: ");
  Serial.println(WiFi.localIP());
 
  Serial.println("Timer set to 5 seconds (timerDelay variable)");
 
 }
 
 int filter(float data){
   static float avg = 0;
   float alpha = 0.1;
 
   avg = ((alpha * data) + ((1. - alpha) * avg));
   
   return (int)avg;
 }
 void httpss(int db){
  if(WiFi.status()== WL_CONNECTED){
      WiFiClient client;
      HTTPClient http;

     
      
      // Your Domain name with URL path or IP address with path
      http.begin(client, serverName);
      http.addHeader("Content-Type", "application/json");
     int httpResponseCode = http.POST("{\"uuid\":\"cac1010b-fa6e-4641-9d95-ba82ec4e5d27\",\"decibel\":"+ String(db) +"}");
      // Send HTTP GET request
//     Serial.println(httpResponseCode);
      // Free resources
      http.end();
    }
    else {
      Serial.println("WiFi Disconnected");
    }
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
  if ((millis() - lastTime) > timerDelay) {
    //Check WiFi connection status
     httpss(db); 
     lastTime = millis();
    }
    
   
  
     
     
  
 
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
