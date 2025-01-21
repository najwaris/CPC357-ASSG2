/*
Smart Indoor Air Quality Monitoring and Alert System - Assignment 2
*/

#include <WiFi.h>
// #include <WiFiClientSecure.h>
#include <PubSubClient.h>
#include "DHT.h"
#define DHTTYPE DHT11

// WiFi credentials
const char* WIFI_SSID = "HouseMates";
const char* WIFI_PASSWORD = "csweet950805";

const char* MQTT_USERNAME = "CPC357_ASG2";
const char* MQTT_PASSWORD = "iffnaj357";

// GCP MQTT details
const char* MQTT_SERVER = "34.171.140.11";
const char* MQTT_TOPIC = "iot";
const int MQTT_PORT = 1883;

// Used Pins
const int dht11Pin = 42;
const int mq2Pin = 4;
const int redLedPin = 9;
const int greenLedPin = 5;
const int buzzerPin = 12;
const int relayPin = 39;
// const int propellerPin = X;
const int buttonPin = 38;

// Threshold value
const float HUMIDITY_MAX_THRESHOLD = 80.0;
const float HUMIDITY_MIN_THRESHOLD = 30.0;
const int TEMPERATURE_THRESHOLD = 35;
const int GAS_THRESHOLD = 300;

// Input sensor definitions
DHT dht(dht11Pin, DHTTYPE);

WiFiClient espClient;
PubSubClient client(espClient);
// WiFiClientSecure espClientSecure;
// PubSubClient client(espClientSecure);

unsigned long sensorInterval = 900000;  // 15 minutes by default
unsigned long lastMsgTime = 0;
unsigned long buzzerStartTime = 0;

// flag for logic in the system
bool buzzerActive = false;
bool propellerActive = false;
bool propellerManualOverride = false;

void setup_wifi() {
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(WIFI_SSID);

  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  while (!client.connected()) {
    Serial.println("Attempting MQTT connection...");
    if (client.connect("ESP32Client", MQTT_USERNAME, MQTT_PASSWORD)) {
      Serial.println("Connected to MQTT broker!");
    } else {
      Serial.print("Failed, rc=");
      Serial.print(client.state());
      Serial.println(" Retrying in 5 seconds...");
      delay(5000);
    }
  }
}

void handleBuzzer() {
  if (buzzerActive) {
    if (millis() - buzzerStartTime > 2000) {
      noTone(buzzerPin);
      buzzerActive = false;
    }
  }
}

void setup() {
  Serial.begin(115200);
  dht.begin();

  // Initialize sensors
  pinMode(mq2Pin, INPUT);
  pinMode(redLedPin, OUTPUT);
  pinMode(greenLedPin, OUTPUT);
  pinMode(buzzerPin, OUTPUT);
  pinMode(relayPin, OUTPUT);
  pinMode(buttonPin, INPUT_PULLUP);  // External button with pull-up resistor

  // Set initial states
  digitalWrite(redLedPin, LOW);
  digitalWrite(greenLedPin, LOW);
  digitalWrite(buzzerPin, LOW);
  digitalWrite(relayPin, false);  // Ensure propelleer is OFF at startup

  setup_wifi();
  client.setServer(MQTT_SERVER, MQTT_PORT);
}

void loop() {

  if (!client.connected()) {
    reconnect();
  }

  client.loop();
  handleBuzzer();

  // Read and send sensor data at regular intervals
  unsigned long cur = millis();
  if (cur - lastMsgTime >= sensorInterval || lastMsgTime == 0) {
    lastMsgTime = cur;

    // Read data from DHT11
    float humidity = dht.readHumidity();
    int temperature = dht.readTemperature();

    // Read data from MQ2
    int gasValue = analogRead(mq2Pin);

    // Create a JSON-like payload
    char payload[256];
    snprintf(payload, sizeof(payload),
             "{\"Humidity\": %.2f, \"Temperature\": %d, \"Gas\": %d}",
             humidity, temperature, gasValue);

    // Publish data to GCP MQTT topic
    client.publish(MQTT_TOPIC, payload);
    Serial.println("Published payload:");
    Serial.println(payload);

    // Determine safety, trigger alerts and set interval accordingly
    if (gasValue > GAS_THRESHOLD || humidity < HUMIDITY_MIN_THRESHOLD || humidity > HUMIDITY_MAX_THRESHOLD || temperature > TEMPERATURE_THRESHOLD) {

      // Turn on the propeller if these conditions are met
      if (humidity < HUMIDITY_MIN_THRESHOLD || temperature > TEMPERATURE_THRESHOLD || gasValue > GAS_THRESHOLD) {

        digitalWrite(relayPin, true);
        propellerActive = true;

        sensorInterval = 300000;         // Switch to 5 minutes
        digitalWrite(redLedPin, HIGH);   // Turn on Red LED
        digitalWrite(greenLedPin, LOW);  // Turn off Green LED

        if (!buzzerActive) {
          tone(buzzerPin, 2000);
          buzzerStartTime = millis();
          buzzerActive = true;
        }
      } else {

        // Skip propeller if it doesnt meet the conditions
        sensorInterval = 300000;         // Switch to 5 minutes
        digitalWrite(redLedPin, HIGH);   // Turn on Red LED
        digitalWrite(greenLedPin, LOW);  // Turn off Green LED

        if (!buzzerActive) {
          tone(buzzerPin, 2000);
          buzzerStartTime = millis();
          buzzerActive = true;
        }
      }
    } else {

      // Safe conditions
      sensorInterval = 900000;          // Switch back to 15 minutes
      digitalWrite(redLedPin, LOW);     // Turn off Red LED
      digitalWrite(greenLedPin, HIGH);  // Turn on Green LED

      // Ensure buzzer is off
      noTone(buzzerPin);
      buzzerActive = false;

      // Turn off propeller if button is pressed
      if (!digitalRead(buttonPin)) {
        digitalWrite(relayPin, false);
        propellerActive = false;
      }
    }
  }

  // Turn off propeller manually
  if (!digitalRead(buttonPin) && propellerActive) {
    digitalWrite(relayPin, false);
    propellerActive = false;
  }
}
