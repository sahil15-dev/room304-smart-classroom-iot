#include <Arduino.h>
#include <DHT.h>
#include <math.h>
#include "config.h"

// Protocol: DATA,temp,humidity,light,sound_span,door_open,expected_empty,alert,pir
// Alert: 0 normal; 1 comfort; 2 possible lighting waste; 3 DHT read failure.
// This is a low-voltage observational prototype, NOT a true occupancy or energy meter.

DHT dht(DHTPIN, DHTTYPE);
unsigned long lastReportMs = 0;
unsigned long lastActivityMs = 0;
unsigned long lastBuzzerMs = 0;
unsigned long lastDebounceMs = 0;
unsigned long buzzerOffAtMs = 0;
bool expectedEmpty = false;
bool previousButtonRaw = HIGH;
bool stableButtonRaw = HIGH;
bool previousReedRaw = HIGH;
bool buzzerOn = false;
int previousAlertCode = 0;

bool buttonPressed(bool raw) {
  return BUTTON_PRESSED_IS_LOW ? raw == LOW : raw == HIGH;
}

bool doorIsOpen(bool raw) {
  return REED_CLOSED_IS_LOW ? raw == HIGH : raw == LOW;
}

bool roomIsBright(int value) {
  return LIGHT_BRIGHT_IS_HIGH ? value >= LIGHT_BRIGHT_THRESHOLD
                              : value <= LIGHT_BRIGHT_THRESHOLD;
}

void setRgb(bool r, bool g, bool b) {
  digitalWrite(PIN_LED_R, (r != RGB_COMMON_ANODE) ? HIGH : LOW);
  digitalWrite(PIN_LED_G, (g != RGB_COMMON_ANODE) ? HIGH : LOW);
  digitalWrite(PIN_LED_B, (b != RGB_COMMON_ANODE) ? HIGH : LOW);
}

void setBuzzer(bool active) {
  digitalWrite(PIN_BUZZER, (active != BUZZER_ACTIVE_LOW) ? HIGH : LOW);
  buzzerOn = active;
}

int sampleSoundSpan() {
  int low = 1023, high = 0;
  unsigned long beginMs = millis();
  while (millis() - beginMs < 35UL) {
    int v = analogRead(PIN_SOUND);
    if (v < low) low = v;
    if (v > high) high = v;
  }
  return high - low;
}

void updateButton(unsigned long nowMs) {
  bool raw = digitalRead(PIN_MODE_BUTTON);
  if (raw != previousButtonRaw) lastDebounceMs = nowMs;
  if (nowMs - lastDebounceMs >= BUTTON_DEBOUNCE_MS && raw != stableButtonRaw) {
    stableButtonRaw = raw;
    if (buttonPressed(raw)) {
      expectedEmpty = !expectedEmpty;
      lastActivityMs = nowMs;
      Serial.print(F("INFO,expected_empty="));
      Serial.println(expectedEmpty ? 1 : 0);
    }
  }
  previousButtonRaw = raw;
}

void updateBuzzer(unsigned long nowMs, int alert) {
  if (buzzerOn && (long)(nowMs - buzzerOffAtMs) >= 0) setBuzzer(false);
  if (alert == 0) {
    if (buzzerOn) setBuzzer(false);
    previousAlertCode = 0;
    return;
  }
  // Beep immediately on a new/changed warning, then at most every 15 sec.
  bool freshAlert = alert != previousAlertCode;
  if (!buzzerOn && (freshAlert || nowMs - lastBuzzerMs >= BUZZER_INTERVAL_MS)) {
    setBuzzer(true);
    buzzerOffAtMs = nowMs + BUZZER_ON_MS;
    lastBuzzerMs = nowMs;
  }
  previousAlertCode = alert;
}

void setup() {
  Serial.begin(9600);
  pinMode(PIN_REED, INPUT_PULLUP);
  pinMode(PIN_MODE_BUTTON, INPUT_PULLUP);
  pinMode(PIN_BUZZER, OUTPUT);
  pinMode(PIN_LED_R, OUTPUT);
  pinMode(PIN_LED_G, OUTPUT);
  pinMode(PIN_LED_B, OUTPUT);
  if (ENABLE_PIR) pinMode(PIN_PIR, INPUT);
  setBuzzer(false);
  setRgb(false, true, false);
  dht.begin();

  previousButtonRaw = digitalRead(PIN_MODE_BUTTON);
  stableButtonRaw = previousButtonRaw;
  previousReedRaw = digitalRead(PIN_REED);
  lastReportMs = millis();
  lastActivityMs = millis();
  Serial.println(F("INFO,Room304 ready; PIR disabled"));
  Serial.println(F("INFO,DATA,temp,humidity,light,sound_span,door_open,expected_empty,alert,pir"));
}

void loop() {
  unsigned long nowMs = millis();
  updateButton(nowMs);
  // Unblock the buzzer promptly between DHT readings.
  if (buzzerOn && (long)(nowMs - buzzerOffAtMs) >= 0) setBuzzer(false);
  if (nowMs - lastReportMs < REPORT_INTERVAL_MS) return;
  lastReportMs = nowMs;

  float temp = dht.readTemperature();
  float humidity = dht.readHumidity();
  int light = analogRead(PIN_LIGHT);
  int sound = sampleSoundSpan();
  bool reedRaw = digitalRead(PIN_REED);
  bool doorOpen = doorIsOpen(reedRaw);
  bool pirMotion = ENABLE_PIR ? digitalRead(PIN_PIR) == HIGH : false;

  if (reedRaw != previousReedRaw || sound > SOUND_ACTIVITY_THRESHOLD || pirMotion) {
    lastActivityMs = nowMs;
  }
  previousReedRaw = reedRaw;

  bool sensorFault = isnan(temp) || isnan(humidity);
  bool comfortAlert = !sensorFault && (temp < TEMP_MIN_C || temp > TEMP_MAX_C ||
                                       humidity < HUM_MIN_PERCENT || humidity > HUM_MAX_PERCENT);
  bool lightingAlert = expectedEmpty && roomIsBright(light) &&
                       (nowMs - lastActivityMs >= QUIET_PERIOD_MS);
  int alert = sensorFault ? 3 : (lightingAlert ? 2 : (comfortAlert ? 1 : 0));

  if (alert == 0) setRgb(false, true, false);       // green
  else if (alert == 1) setRgb(false, false, true);  // blue
  else setRgb(true, false, false);                  // red
  updateBuzzer(nowMs, alert);

  Serial.print(F("DATA,"));
  if (sensorFault) Serial.print(F("nan,nan"));
  else {
    Serial.print(temp, 1);
    Serial.print(',');
    Serial.print(humidity, 1);
  }
  Serial.print(','); Serial.print(light);
  Serial.print(','); Serial.print(sound);
  Serial.print(','); Serial.print(doorOpen ? 1 : 0);
  Serial.print(','); Serial.print(expectedEmpty ? 1 : 0);
  Serial.print(','); Serial.print(alert);
  Serial.print(','); Serial.println(pirMotion ? 1 : 0);
}
