#include "WiFi.h" // ESP32 WiFi include
#include <DHT.h>
#define DHTPIN 25
#define DHTTYPE DHT11
const uint16_t port = 8090;
const char * host = "192.168.104.86";
float valueBright;
float valuewaterLevelSensor;
int temperatureRoomSensor;
int humidityRoomSensor;
float valuehumidityGroundSensor;
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
  WiFi.begin("galaxy", "king2907");

  uint8_t i = 0;
  while (WiFi.status() != WL_CONNECTED){
  }

  Serial.println(WiFi.localIP());
}

void loop()
{
  if (!client.connect(host, port)) {
    Serial.println("connection failed");
    delay(2000);
    return;
  }

  valueBright = analogRead(35);  int brightSensor = (int) ((valueBright / 4095) *100); brightSensor = 100 - brightSensor; 
  valuewaterLevelSensor = analogRead(32); int waterLevelSensor = (int) ((valuewaterLevelSensor - 2700 )/800 *100); 
  temperatureRoomSensor = dht.readTemperature(); 
  humidityRoomSensor = dht.readHumidity(); 
  valuehumidityGroundSensor = analogRead(34); int humidityGroundSensor = (int) ((valuehumidityGroundSensor / 1350) *100); 
  if (client.connected() && temperatureRoomSensor != 2147483647) {
    client.println(String(brightSensor) + ";" + String(waterLevelSensor) + ";" + String(temperatureRoomSensor) + ";" + String(humidityRoomSensor) + ";" + String(humidityGroundSensor) + ";" + "#");
  }
  delay(30000);
}
