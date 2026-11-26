# Scope and limitations

## Scope

Smart Classroom Sentinel monitors physical conditions and activity clues through low-voltage sensors. It implements local warnings, records accepted readings, uploads them to ThingSpeak and serves a read-only dashboard using Flask.

**Deliberately out of scope:** direct control of classroom lights, power outlets, HVAC or mains circuits; measuring actual power consumption; audio recording; facial recognition; confirmed presence/head counting; and unattended automatic decisions about real building equipment.

## Engineering trade-offs

| Design choice | Benefit | Limitation |
|:--|:--|:--|
| Arduino UNO + USB serial | Accessible hardware and straightforward debugging | Requires a connected laptop for cloud updates |
| Private ThingSpeak channel | Timestamped, low-cost cloud storage | Rate limits and near-real-time, not continuous streaming |
| Render-hosted Flask frontend | Accessible monitoring view without a local web server | Free instance startup delays; Basic Auth session behavior |
| Relative LDR measurement | Simple light-condition comparison | ADC is not a calibrated lux reading |
| Analog microphone span | Indicates changes without storing raw audio | Weak sensitivity on some modules; never decibels |
| PIR + reed switch | Non-camera motion/door cues | No guaranteed detection of stationary people |
| Expected-empty button | Explicit operating context for lighting warnings | Does not establish that room is actually empty |

## Reliability and interpretation

A warning is an observation-based indication for a responsible person to verify. Sensor values may drift because of supply voltage, mounting, modules or ambient conditions. False positives/negatives are possible. The local buzzer and RGB LED are independent of internet connectivity; the cloud display is not.

Public repository code contains generic configuration templates and sanitized graphics. No credentials are required to review the source. Individual classroom deployments must obtain appropriate consent before collecting or publishing sensitive location or occupancy-related data.
