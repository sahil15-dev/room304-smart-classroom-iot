# Complete build guide — Room 304 Smart Classroom

Follow these phases in order. Mark a phase complete **only after observing its pass criterion on your actual hardware**.

## Phase 0 — Gather and identify

- [ ] Arduino UNO R3 and USB data cable; Windows laptop; internet connection.
- [ ] Arduino Sensor Kit modules: Temp and humidity, Photoresistor, Big Sound, Mini Reed, Button, RGB LED/SMD RGB, Active Buzzer.
- [ ] Breadboard and ~20–30 jumpers; resistor set if RGB module needs external current limiting.
- [ ] Confirm pin order and module ratings from printed markings. PIR not needed.
- [ ] Take photo of module labels/pinouts.

**Pass:** every board is identified, no visible damage, and there is a wiring plan.

## Phase 1 — Install software and test Arduino alone

1. Install Arduino IDE, or VS Code with PlatformIO IDE extension.
2. Connect UNO via USB and select board **Arduino Uno**, then its COM port.
3. Upload built-in Blink. Onboard LED should blink.
4. Install Adafruit's `DHT sensor library` and `Adafruit Unified Sensor`.
5. Open `firmware/Room304/Room304.ino` (Arduino IDE) OR open repo root in VS Code and use PlatformIO.
6. Verify `config.h`: DHT sensor type, module logic polarities, light threshold direction and `ENABLE_PIR = false`.

**Pass:** Arduino uploads without error. If not, check COM/USB cable, board, driver and library manager.

## Phase 2 — Connect core sensors one by one (USB OFF while wiring)

1. UNO GND to breadboard ground rail; UNO 5V to positive rail. Ensure rails aren't unexpectedly split.
2. Temp/humidity `S` to D2; module-rated `+` to VCC and `-` to ground. Upload and validate readings.
3. Photoresistor analog output to A0, module power/ground. Cover then shine phone torch, record relative readings.
4. Big Sound analog output AO to A1 (not digital DO). Clap near microphone versus quiet.
5. Mini Reed signal to D3, module power/ground. Move magnet; record status change.
6. Button signal to D4, module power/ground. A single press should toggle expected-empty.

**Pass:** Serial Monitor shows `DATA,...` ~2.5 sec, and each input changes when tested. Check the signal polarity in `config.h` rather than moving random wires.

## Phase 3 — Add local outputs

1. RGB common pin to appropriate common connection, red to D6, green to D9, blue to D10. **Check onboard/current-limiting resistors** and common-anode/cathode design.
2. Active buzzer signal to D5. Power according to its module rating. Verify whether active HIGH or LOW.
3. On a valid normal reading, green should light. Temporarily force a comfort alert with an appropriate test threshold; expect blue and a short beep.
4. Temporarily force a lighting alert using expected-empty mode, bright readings and shorter 30-second quiet period; expect red and brief buzzer.
5. Restore production thresholds and 30-minute quiet interval.

**Pass:** all colors and the buzzer respond correctly, with no GPIO overcurrent or stuck-on buzzer.

## Phase 4 — Calibrate for real classroom conditions

1. For each sensor, capture **at least 10 readings** with time and test conditions.
2. Use `docs/04 Test Plan and Results.md` table to record values.
3. Test photoresistor in dark/ambient/bright. Select `LIGHT_BRIGHT_IS_HIGH` and `LIGHT_BRIGHT_THRESHOLD`.
4. Test Big Sound quiet/talking/clap. Set `SOUND_ACTIVITY_THRESHOLD` above typical baseline if possible.
5. Check DHT temperature and humidity ranges for your actual room; initial limits are placeholders.
6. Test button state, magnet state, and alert priority.
7. Explain false positives; sound + reed are *activity indicators*, not definite occupancy evidence.

**Pass:** thresholds are justified by measured data; repeatable demo.

## Phase 5 — Run local Python bridge

From repo root in VS Code PowerShell:

```powershell
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python -m bridge.runner --simulate
python -m unittest discover -s tests -v
```

1. Edit `.env` and set `ROOM304_PORT=COM3` or your actual Windows COM port. Leave cloud keys blank initially.
2. **Close Arduino IDE/PlatformIO serial monitor** so Python can open the same port.
3. Run `python -m bridge.runner`.
4. Check terminal output and `data/logs/room304 readings.csv` (ignored by Git).

**Pass:** at least 10 real serial readings written to your local CSV file.

## Phase 6 — ThingSpeak + Telegram

1. Follow `docs/03 Cloud and Alerts.md` to create a private ThingSpeak channel with 8 fields.
2. Copy channel Write API Key into local `.env` (never source code).
3. Restart Python bridge and confirm uploads at 20-second intervals or slower.
4. Configure Telegram only when bot and chat IDs are ready; test alert delivery.
5. Disconnect internet temporarily. Local LED/buzzer should keep working. Restore connection and check next cloud upload.

**Pass:** live dashboard entries and, if enabled, real Telegram alert. Capture screenshots without tokens.

## Phase 7 — Assemble and present

1. Mount UNO and sensors on a safe nonconductive base; label each module.
2. Add a cardboard miniature door and magnet for reed demo.
3. Keep DHT away from USB heat and LDR where it sees relevant light.
4. Secure wires, repeat all tests, photograph wiring.
5. Show live values, demonstrate sound, magnet, bright/dark, mode toggle, alerts, dashboard and Telegram.
6. Complete the real-results table. Do not substitute sample readings from simulation.

**Pass:** two consecutive complete demo rehearsals and fully documented results.

## Phase 8 — PIR upgrade next week, not now

When a real HC-SR501 is available, confirm its voltage and output specification. Connect `OUT -> D7`, rated `VCC -> 5V`, `GND -> GND`. In `config.h`, change **only** `ENABLE_PIR = true` initially. Allow warm-up, calibrate sensitivity/hold time, then record new observations. The existing `DATA` protocol already has `pir_motion` as the last field. Compare false alerts with and without PIR. Do not claim motion detection proves presence or absence.
