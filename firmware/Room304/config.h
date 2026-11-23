#ifndef ROOM304_CONFIG_H
#define ROOM304_CONFIG_H

// Room 304 Smart Classroom: adjust after validating your OWN modules.
// Hardware target: classic 5 V Arduino UNO R3.

#define DHTPIN 2
#define DHTTYPE DHT11  // Change to DHT22 only if that is your sensor.

const byte PIN_REED = 3;
const byte PIN_MODE_BUTTON = 4;
const byte PIN_BUZZER = 5;
const byte PIN_LED_R = 6;
const byte PIN_PIR = 7;              // RESERVED for next week's optional PIR.
const byte PIN_LED_G = 9;
const byte PIN_LED_B = 10;
const byte PIN_LIGHT = A0;
const byte PIN_SOUND = A1;

// PIR remains OFF in this version. No PIR connection is required.
const bool ENABLE_PIR = false;

// Modules vary; verify their signal states before changing these defaults.
const bool BUTTON_PRESSED_IS_LOW = true;
const bool REED_CLOSED_IS_LOW = true;
const bool RGB_COMMON_ANODE = false;
const bool BUZZER_ACTIVE_LOW = false;
const bool LIGHT_BRIGHT_IS_HIGH = false;  // Verify with flashlight and cover tests.

const unsigned long REPORT_INTERVAL_MS = 2500UL;
const unsigned long QUIET_PERIOD_MS = 1800000UL;  // 30 minutes; test with 30000UL.
const unsigned long BUZZER_INTERVAL_MS = 15000UL;
const unsigned long BUZZER_ON_MS = 120UL;
const unsigned long BUTTON_DEBOUNCE_MS = 50UL;

// Starting values ONLY. Calibrate using recorded classroom readings.
const int LIGHT_BRIGHT_THRESHOLD = 700;
const unsigned long SOUND_WINDOW_MS = 250UL;  // Non-blocking microphone windows.
const int SOUND_ACTIVITY_THRESHOLD = 60;  // Calibrate from actual quiet vs loud spans.
const float TEMP_MIN_C = 18.0;
const float TEMP_MAX_C = 28.0;
const float HUM_MIN_PERCENT = 30.0;
const float HUM_MAX_PERCENT = 70.0;

#endif
