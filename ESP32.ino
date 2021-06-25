#include "WiFi.h" // ESP32 WiFi include
#include <DHT.h>
#define DHTPIN 25
#define DHTTYPE DHT11
const uint16_t port = 8090;
const char * host = "172.16.151.125";
float valueBright;
float valuewaterLevelSensor;
int temperatureRoomSensor;
int humidityRoomSensor;
float valuehumidityGroundSensor;
float minore = 2700;
float maggiore = 3500;
WiFiClient client;
DHT dht(DHTPIN, DHTTYPE);

void setup()
{
  dht.begin();
  ConnectToWiFi();
}
void ConnectToWiFi()
{
  WiFi.mode(WIFI_STA);
  WiFi.begin("Perry", "trattore");

  uint8_t i = 0;
  while (WiFi.status() != WL_CONNECTED){
  }
}

void loop()
{
  WiFiClient client;
  if (!client.connect(host, port)) {
    delay(2000);
    return;
  }

  valueBright = analogRead(35);  int brightSensor = (int) ((valueBright / 4095) *100); brightSensor = 100 - brightSensor; 
  valuewaterLevelSensor = analogRead(32); 
  int waterLevelSensor = 0;
  if(valuewaterLevelSensor >=minore){
    waterLevelSensor = (int) (((valuewaterLevelSensor-minore)/(maggiore-minore))*100); 
  }
  temperatureRoomSensor = dht.readTemperature(); 
  humidityRoomSensor = dht.readHumidity(); 
  valuehumidityGroundSensor = analogRead(34); int humidityGroundSensor = (int) ((valuehumidityGroundSensor / 1350) *100); 
  if (client.connected()) {
    client.print(String(brightSensor) + ";" + String(waterLevelSensor) + ";" + String(temperatureRoomSensor) + ";" + String(humidityRoomSensor) + ";" + String(humidityGroundSensor) + ";" + "#");
  }
  delay(30000);
}