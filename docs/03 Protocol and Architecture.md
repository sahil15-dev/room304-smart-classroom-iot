# Protocol and architecture

![System architecture](../assets/system%20architecture.png)

## Serial protocol

At 9600 baud, the UNO periodically emits:

```text
INFO,Room304 ready; PIR enabled on D7
INFO,DATA,temp,humidity,light,sound_span,door_open,expected_empty,alert,pir
DATA,21.7,32.0,635,2,1,0,0,1
```

The last line is an **illustrative structure** consistent with a previously observed integration reading. The comma-separated values map to eight fields: temperature °C, relative humidity %, light ADC, sound span, door-open binary, expected-empty binary, alert code and PIR motion binary.

The Python protocol parser rejects malformed or out-of-range records. A missing DHT value is encoded as `nan` with alert code 3. Numeric brightness is a sensor-specific 0–1023 analog value; it is not lux.

## Cloud fields

| ThingSpeak field | Column | Meaning |
|:--|:--|:--|
| Field 1 | `temperature_c` | Temperature in °C |
| Field 2 | `humidity_percent` | Relative humidity in % |
| Field 3 | `light` | Relative ambient light ADC |
| Field 4 | `sound_span` | Peak-to-peak analog amplitude |
| Field 5 | `door_open` | Reed input state, 0 or 1 |
| Field 6 | `expected_empty` | Operator-selected state, 0 or 1 |
| Field 7 | `alert_code` | 0 normal, 1 comfort, 2 possible lighting waste, 3 DHT fault |
| Field 8 | `pir_motion` | PIR digital output, 0 or 1 |

## Timing and display

- Arduino reports approximately every 2.5 seconds, with non-blocking sound sampling in 250 ms windows.
- Python bridge logs each accepted serial record and attempts cloud updates at intervals of at least 20 seconds.
- Hosted overview reads a shorter recent sample set (up to 160 records) to reduce rendering work; Data History loads a larger set on demand (up to 800).
- The hosted backend caches recent ThingSpeak reads for about 10 seconds. A recent cloud value may therefore be tens of seconds behind the Arduino and must not be described as instant streaming.
- A disconnected bridge does not prevent viewing already stored history, but the dashboard must label stale data accordingly.

## Alert logic

The `expected_empty` button is an operator-set expectation. A possible lighting-waste warning requires all of the following: expected-empty mode, sufficiently bright readings, and no recorded activity during the configured quiet interval (default 30 minutes). Activity clues can include sound above a threshold, PIR output or a reed-state change. The system intentionally does not infer confirmed human occupancy.

Comfort alerts use upper/lower temperature and humidity values in `config.h`; hardware faults take precedence over other alerts. Local LEDs/buzzer operate on the Arduino even if the cloud service is unavailable.
