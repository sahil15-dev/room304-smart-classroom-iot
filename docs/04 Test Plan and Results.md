# Actual test plan and results — fill during lab

**Never treat illustrative/simulated readings as measured lab data.** Add date, environment, photos and raw readings from your own sensors.

| Test case | Procedure | Expected | Actual result / timestamp | Pass? |
| --- | --- | --- | --- | --- |
| Arduino upload | Blink / upload firmware | Board responds | TBD | [ ] |
| DHT temperature | Record 10 readings | Plausible °C | TBD | [ ] |
| DHT humidity | Record 10 readings | Plausible % | TBD | [ ] |
| LDR dark | Cover module | Changes reading | TBD | [ ] |
| LDR bright | Phone flashlight | Changes reading | TBD | [ ] |
| Big Sound quiet | Baseline 10 readings | Low span | TBD | [ ] |
| Big Sound clap | Repeat clap | Higher span | TBD | [ ] |
| Mini Reed closed | Magnet nearby | Door state switches | TBD | [ ] |
| Mini Reed open | Magnet away | Opposite state | TBD | [ ] |
| Expected-empty button | Toggle twice | 0→1→0 | TBD | [ ] |
| Green normal state | Valid room | Green only | TBD | [ ] |
| Blue comfort state | Calibrated temp/humidity test | Blue + brief buzzer | TBD | [ ] |
| Red possible lighting state | Mode on + bright + timed quiet (accelerated demo) | Red + brief buzzer | TBD | [ ] |
| Sensor fault | Disconnect DHT with USB OFF, reconnect safely | Alert 3 and red | TBD | [ ] |
| Python CSV logging | 10 readings | Timestamps and all fields | TBD | [ ] |
| ThingSpeak | 10 uploads | Cloud entries and charts | TBD | [ ] |
| Telegram | Trigger anomaly | Message arrives | TBD | [ ] |
| Offline internet | Disable laptop internet | Local outputs still work | TBD | [ ] |

## Calibration record

- DHT model printed on module: ______
- Photoresistor light input direction: higher / lower when bright ______
- Photoresistor dark / ambient / bright (10 readings): ______ / ______ / ______
- Big Sound quiet / talking / clap (10 readings): ______ / ______ / ______
- D3 magnet-near input: HIGH / LOW ______
- Button press input: HIGH / LOW ______
- RGB module: common cathode / anode ______
- Buzzer active state: HIGH / LOW ______
- Final light threshold: ______
- Final sound threshold: ______
- Final comfort min/max T and RH: ______
- Serial port: ______
- ThingSpeak channel ID (not Write key): ______
- Photos of wiring/screenshots saved under: ______

## Reflection and limitations

Explain at least one false alert or missing activity event. The sensors provide indirect activity indications, not certified occupancy or actual kWh data. Do not claim energy saved unless a separate physical energy measurement exists.
