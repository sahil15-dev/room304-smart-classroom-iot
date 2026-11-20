# Wiring inspection checklist — Room 304

**Target:** Arduino UNO R3, 5 V GPIO, USB laptop power. **PIR not installed.**

## Before wiring (power OFF)

1. Photograph every *actual* module front and back. Printed kit inventories are not sufficient to prove its exact pin order or contents.
2. Identify module name, signal, VCC and GND on the PCB. **Never copy a pin order from a photo of another module.**
3. Use a breadboard or approved low-voltage jumper wires. Connect shared ground first.
4. Check module VCC ratings; apply UNO 5 V only if permitted. Never supply 5 V to a 3.3 V-only module.
5. Verify the RGB board contains appropriate resistors; if using a bare 4-pin LED, add 220–330 ohm in series with *each* color. Ensure a common-cathode module if you leave `RGB_COMMON_ANODE=false`.
6. Ensure buzzer is an *active, low-current GPIO-safe module*. If it needs more current or is a bare buzzer, a proper transistor/driver circuit is required.
7. With the USB disconnected, re-check for wiring shorts, backwards VCC/GND, and loose wires.

## Fixed pin map (PIR optional for future)

| Kit label | Typical module type | Signal | Power/notes |
|---|---|---|---|
| Temp and humidity | DHT11 3-pin (verify!) | D2 | S/+/- to D2/5V/GND; DHT library installed |
| Photoresistor | 3-pin LDR module | A0 | S/+/-; onboard divider normally eliminates a separate 10 kΩ resistor |
| Big Sound | KY-037 style, AO+DO | A1 | **Use AO**, not DO. VCC & GND as labeled |
| Mini Reed | KY-021 style | D3 | Signal may invert with magnet; verify expected closed level |
| Button | 3-pin module | D4 | Signal level on press must be measured/observed |
| Buzzer | Active module | D5 | Signal active level must be verified |
| RGB LED / SMD RGB | 4-pin module | D6 red / D9 green / D10 blue | Confirm resistor support, channel order and common pin |
| PIR | HC-SR501 | D7 reserved | **No PIR this week. Leave D7 disconnected** |

![Pin map](../assets/pin%20map.svg)

## Test each item in order

1. Power Arduino USB; upload built-in Blink first (onboard LED). Disconnect USB again for wiring.
2. Connect temperature/humidity module alone. Upload firmware, read 9600 baud, validate plausible temperature and humidity.
3. Connect photoresistor; cover and illuminate it. Determine whether brightness means higher or lower reading. Set `LIGHT_BRIGHT_IS_HIGH` accordingly.
4. Connect Big Sound AO; quiet-room versus clap. Record 10 readings and calibrate `SOUND_ACTIVITY_THRESHOLD`.
5. Connect Mini Reed; magnet near versus far. Set `REED_CLOSED_IS_LOW` after observing the actual meaning of logic LOW.
6. Connect button; press once, verify `INFO,expected_empty=1`, press again returns 0. If not, verify signal polarity and wiring.
7. Connect RGB; normal green, comfort warning blue, serious/error red. Adjust RGB channel order and common anode/cathode if incorrect.
8. Connect buzzer; confirm alert is brief and not continuously driven. Check active-low/active-high logic and actual current.
9. Only after all sensors work, combine cloud bridge.

## Known hardware caveats

- The photoresistor may be inverted depending on the voltage-divider arrangement. Do NOT trust the numeric threshold without measuring real brightness.
- The Big Sound KY-037 module is suitable for simple **relative analog changes**; its 35 ms sample every 2.5 seconds can miss sounds and cannot directly determine occupancy.
- The Mini Reed detects magnet proximity, not the number of people crossing the doorway.
- A motion sensor added later will still not prove occupancy or emptiness.
- This prototype does not measure watts or kilowatt-hours or switch real classroom electrical circuits.
- Sensors near USB heat, windows or speakers may produce biased readings.
