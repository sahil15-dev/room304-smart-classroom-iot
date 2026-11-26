<p align="center"><img src="assets/project%20banner.png" alt="Smart Classroom Sentinel" width="100%"></p>

<h1 align="center">Smart Classroom Sentinel</h1>
<p align="center"><strong>Room 304 · Smart environment monitoring and possible-energy-waste detection</strong></p>
<p align="center">
  <a href="https://smart-classroom-sentinel.onrender.com/">Hosted dashboard</a> ·
  <a href="docs/02%20Setup%20and%20Operation.md">Setup</a> ·
  <a href="docs/04%20Calibration%20and%20Verification.md">Calibration</a> ·
  <a href="docs/05%20Hosting%20and%20Security.md">Deployment</a>
</p>

A working **Arduino UNO + Python + ThingSpeak + Flask** prototype that observes classroom conditions, logs measurements and flags comfort or possible lighting-waste conditions. The system provides a local RGB LED/buzzer response and a password-protected cloud dashboard with recent readings, trends and history.

It is an **observational** project: it does not measure energy consumption, count people, record speech, or operate building lighting/HVAC equipment.

## Project overview

<p align="center"><img src="assets/system%20architecture.png" alt="Room 304 sensor-to-cloud architecture" width="100%"></p>

| Layer | Implementation | What it does |
|:--|:--|:--|
| Sensors | DHT11, photoresistor, analog sound, reed switch, PIR, mode button | Observe classroom environment and activity clues |
| Embedded | Arduino UNO R3 / PlatformIO | Sample sensors, evaluate warning rules, drive RGB LED and buzzer |
| Bridge | Python / pyserial | Read USB serial, validate the protocol, write local CSV, upload to ThingSpeak |
| Cloud | Private ThingSpeak channel | Hold eight timestamped sensor fields |
| Dashboard | Flask / Render | Serve a read-only, authenticated website with overview, trends, tests and history |

## Dashboard

<p align="center"><img src="assets/dashboard%20preview.png" alt="Screenshot of the deployed Smart Classroom Sentinel overview" width="94%"></p>
<p align="center"><sub>Actual hosted-dashboard screenshot captured during integration; visible values and labels reflect that point in development, not the current live state.</sub></p>

**Hosted site:** [smart-classroom-sentinel.onrender.com](https://smart-classroom-sentinel.onrender.com/) (credentials required). The website remains available when the laptop is off, but **fresh measurements stop until the Arduino and bridge resume**. Cloud refresh is near-real-time, not instant streaming.

### Hardware and alert behavior

| Signal | Pin | Function |
|:--|:--|:--|
| Temperature + relative humidity | D2 | DHT11 comfort readings |
| Door contact | D3 | Reed switch open/close indication |
| Expected-empty mode | D4 | Local button; operator-selected state, **not proof of vacancy** |
| Buzzer | D5 | Short local warning sound |
| RGB LED | D6 / D9 / D10 | Red / green / blue warning display |
| PIR motion | D7 | Detects motion output, not a headcount |
| Ambient light | A0 | Relative brightness; current module reads **lower ADC when brighter** |
| Sound activity | A1 | Analog peak-to-peak span, **not decibels or recorded audio** |

![Alert reference](assets/alert%20reference.png)

- **Green / code 0:** readings inside configured rules.
- **Blue / code 1:** temperature or humidity outside configured comfort ranges.
- **Red / code 2:** potential unnecessary lighting *if* the room is marked expected-empty, remains bright and no activity is detected for the configured quiet period.
- **Red / code 3:** DHT sensor reading fault.

The factory-style starting thresholds in `firmware/Room304/config.h` are configurable and should be evaluated against the physical installation. Activity signals can miss stationary people; a lighting warning is a **prompt to check**, not a definitive energy-waste finding.

## Complete wiring blueprint

![Room 304 complete wiring diagram](assets/wiring%20blueprint.png)

The [editable Cirkit Designer circuit](assets/room%20304%20circuit.ckt) is included alongside the exported diagram. It documents the Arduino UNO R3, breadboard, DHT11, reed switch, pushbutton, buzzer, RGB LED, PIR, light sensor and analog sound sensor in the physical prototype. The connections correspond to the pin assignments in [`config.h`](firmware/Room304/config.h). Verify actual module labels and polarity before wiring, as module pin orders can differ.

**DHT11 as built:** This prototype used a four-pin DHT11 without an added external DATA pull-up resistor; VCC connects to 5 V, DATA to D2 and GND to ground, while the unused pin is left open. This reflects the assembled prototype, rather than a universal recommendation. For reliable operation of a bare DHT11 in other builds, a pull-up between DATA and VCC may be necessary depending on the sensor, cable length and circuit implementation.

## Hardware prototype

<p align="center"><img src="assets/hardware%20prototype.jpg" alt="Physical Arduino sensor prototype on a breadboard" width="48%"></p>
<p align="center"><sub>Photograph of the assembled Arduino sensor prototype during development.</sub></p>

## Quick start

**Requirements:** Arduino UNO with the wired sensors; Python 3.10+; PlatformIO (Arduino firmware); USB serial port; optional ThingSpeak channel for cloud mode.

1. Build/upload `firmware/Room304/Room304.ino` using `platformio.ini` and check the correct COM port.
2. Install dependencies and configure the local `.env` from `.env.example` (private keys must never be committed).

```powershell
python -m pip install -r requirements.txt -r dashboard/requirements.txt
Copy-Item .env.example .env
# Set ROOM304_PORT and, for cloud uploads, THINGSPEAK_WRITE_KEY in .env.
```

3. **Close PlatformIO Serial Monitor**, then start the bridge:

```powershell
python -m bridge.runner
```

4. To use the local dashboard, set `DASHBOARD_DATA_SOURCE=local` in `.env` and start a second terminal:

```powershell
python -m dashboard.app
```

Visit `http://127.0.0.1:5000`. For the already-hosted site, the Flask process is not needed on the laptop; the bridge supplies fresh readings to ThingSpeak.

For no-hardware protocol testing: `python -m bridge.runner --simulate` creates **clearly labeled simulated local data**, not cloud or physical test evidence.

## Documentation

| Document | Contents |
|:--|:--|
| [Hardware and wiring](docs/01%20Hardware%20and%20Wiring.md) | Modules, pinout, voltage and electrical safety |
| [Setup and operation](docs/02%20Setup%20and%20Operation.md) | Installation, bridge, local dashboard and troubleshooting |
| [Protocol and architecture](docs/03%20Protocol%20and%20Architecture.md) | Serial format, cloud mapping, alert logic and timing |
| [Calibration and verification](docs/04%20Calibration%20and%20Verification.md) | Physical tests, thresholds and known measurement constraints |
| [Hosting and security](docs/05%20Hosting%20and%20Security.md) | Render settings, credentials and deployment architecture |
| [Design limits](docs/06%20Scope%20and%20Limitations.md) | Explicit scope, trade-offs and safety constraints |
| [Demo guide](docs/07%20Demonstration.md) | Reproducible demonstrations and evidence expectations |

## Testing

The repository includes offline protocol, dashboard and access-control tests and a GitHub Actions workflow.

```powershell
python -m unittest discover -s tests -v
```

Offline tests verify software behavior; they do not establish the accuracy or reliability of physical sensors. Recorded classroom readings and the hosted integration were observed during development; calibration evidence should accompany claims about sound sensitivity or occupancy-related alerts.

## Repository layout

```text
assets/                  Visual identity, diagrams (SVG and PNG), dashboard screenshot
bridge/                  USB serial bridge and protocol validation
dashboard/               Flask server, hosted dashboard UI, Dockerfile
docs/                    Final project documentation
firmware/Room304/        Arduino sketch and configuration
.github/workflows/       Automated Python checks
tests/                   Offline regression tests
platformio.ini            PlatformIO UNO configuration
render.yaml              Render hosted-service definition
.env.example             Public config template; actual secrets stay in .env
```

## Privacy and safety

The ThingSpeak **Write API key** is used only by the laptop bridge; the hosted dashboard uses the **Read API key** on the server. Password protection applies to the website, not to repository access. Public source code never requires publishing private keys, student IDs, user credentials or personal data.

All wiring is low-voltage. The system does not connect to or control mains-powered classroom equipment. See [Hosting and Security](docs/05%20Hosting%20and%20Security.md) and [Scope and Limitations](docs/06%20Scope%20and%20Limitations.md).
