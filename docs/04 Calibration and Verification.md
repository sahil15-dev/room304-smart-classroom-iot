# Calibration and verification

This project separates **electrical sensor response** from **physical accuracy**. A dashboard value is not automatically a calibrated quantity.

## Measured integration examples

During the demonstrated classroom session, the bridge received approximately **21.6–21.7 °C**, **31–32% RH**, **633–635 light ADC** and **sound span 2**, together with `door_open=1`, `pir_motion=1` and `alert_code=0`. Successful ThingSpeak uploads were observed. Another hosted capture showed relative humidity **26%** and a comfort warning under the configured 30% lower limit.

These examples demonstrate data flow, not independently certified measurement accuracy or a verified sound response. Thresholds depend on the final sensor placement and installation conditions.

## Calibration method

| Input | Physical comparison | Interpretation |
|:--|:--|:--|
| DHT11 | Stabilize 3–5 minutes; compare with a known reference device | Typical comfort monitoring; do not claim precision beyond sensor specification |
| LDR | Record covered / normal lights / flashlight values | On the present module, **lower ADC means brighter**; select a threshold separating the intended lighting states |
| Sound AO | Record 20–30 s quiet / speech / clapping spans | If quiet and loud spans overlap, hardware response is insufficient; changing the threshold will not fix sensitivity |
| PIR | Wait after powering up; still → walk → allow to reset | Output must show a genuine HIGH and LOW in suitable conditions |
| Reed | Move magnet to near/away positions | Confirm the signal toggles and door labels match physical placement |
| Button | Press twice | `expected_empty` toggles 0 → 1 → 0 |
| RGB LED / buzzer | Activate each supported alert under controlled test conditions | Confirm colors and beep correspond to firmware outputs |
| Cloud | Observe a successful bridge upload and the hosted timestamp | Confirm both use the same ThingSpeak channel |

### Sound sensor limitation

Early sound captures were typically only **2–5 ADC span** even when the sensor was expected to detect activity. The sound module must not be represented as an accurate decibel or occupancy sensor. Where loud sound does not separate clearly from quiet, preserve the reading for diagnostics and rely on PIR/door evidence for practical activity checks. The sound threshold in `config.h` is a tunable rule, not a signal-amplification control.

### Light threshold

The firmware uses `LIGHT_BRIGHT_IS_HIGH=false` because the observed LDR output decreases in brighter light. `LIGHT_BRIGHT_THRESHOLD` is evaluated against the actual sensor ADC, with the condition `light <= threshold` treated as bright. A threshold from covered-vs-flashlight measurements is only a starting point; normal classroom lighting is the meaningful reference.

### Alert demonstration

For a controlled comfort example, a temporary threshold can be placed just below the current indoor temperature, causing `alert_code=1` without physically heating the room. For a lighting demonstration, shortening the quiet interval can show `alert_code=2` after an expected-empty mode toggle while the PIR output remains LOW and no other activity is recorded. **Restore normal thresholds and the 30-minute quiet interval after test mode.**

## Acceptance evidence

Representative evidence consists of a wiring photo, relevant serial `DATA` lines, a CSV export, ThingSpeak update timestamps, the hosted dashboard, and observations of physical RGB/buzzer responses. No unrecorded measurements or unverified pass results should be presented as experimentally proven.
