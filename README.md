# Room 304 — Smart Classroom Energy & Comfort Sentinel

A low-voltage **Arduino UNO + Python + ThingSpeak + Telegram** prototype for classroom environmental monitoring. Built around a university Arduino sensor kit. The project monitors temperature, relative humidity, relative light, sound activity, and door state; applies configurable anomaly rules; and can send data to a remote dashboard.

![Architecture overview](assets/system%20architecture.svg)

## Project scope and status

| Feature | Implemented in source | Verified on hardware? |
| --- | --- | --- |
| DHT11 temperature and humidity | Yes | **Not yet** |
| Photoresistor (A0) | Yes | **Not yet** |
| Big Sound analog sensor (A1) | Yes | **Not yet** |
| Mini Reed door input | Yes | **Not yet** |
| RGB LED / buzzer warnings | Yes | **Not yet** |
| Button for expected-empty mode | Yes | **Not yet** |
| Serial-to-CSV bridge | Yes | **Not yet** |
| ThingSpeak HTTP data upload | Yes | **Not yet** |
| Telegram alerts | Yes | **Not yet** |
| PIR motion module | Reserved at D7; **disabled** | **Not installed** |
| Python protocol unit tests | Yes | Run locally to verify |

> **Important:** Source code and simulated data do not prove physical performance. Sensor thresholds, pin markings, RGB/buzzer polarity and real classroom results require on-site verification. This is an activity-indicator and possible-waste alert prototype, not a verified occupancy detector or electrical power meter.

## Hardware

- Arduino UNO R3, USB A–B cable, breadboard, jumpers and laptop.
- From the sensor-kit image: **Temp and humidity**, **Photoresistor**, **Big Sound** (with analog output), **Mini Reed**, **Button**, **RGB LED or SMD RGB**, and **Buzzer** (active type).
- **No PIR sensor for the current build.** D7 is reserved for a future HC-SR501 upgrade.
- Check module pins and voltage ratings before connecting. No mains or HVAC control.

## Wiring summary

| Module | Arduino UNO |
| --- | --- |
| Temp + humidity signal | D2 |
| Mini Reed digital signal | D3 |
| Button digital signal | D4 |
| Active buzzer signal | D5 |
| RGB red | D6 |
| **Reserved PIR** | **D7 — leave disconnected** |
| RGB green | D9 |
| RGB blue | D10 |
| Photoresistor analog signal | A0 |
| Big Sound analog output AO | A1 |
| Module positive power / GND | 5V / GND **only if module ratings allow** |

All grounds must be common. For bare RGB LEDs use individual current-limiting resistors; for module LEDs verify included resistors. See [detailed wiring and inspection](docs/01%20Wiring%20and%20Safety.md) and [pin map](assets/pin%20map.svg).

## Quick start

**Arduino IDE (simplest first run):**

1. Install Arduino IDE and select Board **Arduino Uno** and the right USB COM port.
2. In Library Manager, install **DHT sensor library by Adafruit** and **Adafruit Unified Sensor**.
3. Open `firmware/Room304/Room304.ino`.
4. Inspect `config.h`. Verify DHT11/DHT22, RGB/buzzer/button/reed module polarity, and the light direction.
5. Connect the sensors with USB disconnected, then reconnect USB and upload the program.
6. Open Serial Monitor at **9600 baud**. Readings begin with `DATA,` approximately every 2.5 seconds.

**VS Code + PlatformIO (optional integrated firmware workflow):**

1. Install the official **PlatformIO IDE** VS Code extension.
2. Open this repository folder, not just the `.ino` file.
3. Use the PlatformIO checkmark icon **Build**, arrow icon **Upload**, and plug icon **Monitor**; select the UNO's correct USB port if necessary.
4. All firmware edits use the same canonical `firmware/Room304/Room304.ino` and `config.h`. Do not maintain two different copies.

**Python serial logger and cloud bridge:**

```powershell
python -m pip install -r requirements.txt
Copy-Item .env.example .env
# Edit .env locally; change COM3 and add your cloud/Telegram credentials when ready.
python -m bridge.runner --simulate
python -m unittest discover -s tests -v
python -m bridge.runner
```

The simulation generates **sample data only**, no network calls, at `data/logs/simulated readings.csv` (ignored by Git). Close Arduino Serial Monitor before running the live Python bridge. When no keys are set, the live bridge still prints and logs sensor data.

## Cloud setup

1. Create a private ThingSpeak channel named `Room 304 Smart Classroom` with 8 fields.
2. Obtain your **Write API Key**. Put it in local `.env`, never in source code.
3. For optional Telegram alerts, create a bot with `@BotFather`, start a conversation, and configure its token and chat ID in `.env`.
4. Keep Python running on the laptop; it sends data about every **20 s** and notifications on alarm transitions (with a repeat cooldown).

More: [cloud setup and troubleshooting](docs/03%20Cloud%20and%20Alerts.md).

## Local alarm codes

| Code | LED | Meaning |
| --- | --- | --- |
| 0 | Green | No detected warning |
| 1 | Blue | Temp/humidity outside chosen comfort thresholds |
| 2 | Red | Bright + expected empty + no activity for quiet interval |
| 3 | Red | DHT read error |

Starter thresholds in `config.h` are **examples to calibrate**, not classroom standards. A sound sensor, reed switch, or PIR signal cannot prove that a room is actually unoccupied.

## Project structure

```text
room304 smart classroom iot/
├── firmware/Room304/
│   ├── Room304.ino      # Firmware, sensor logic, LED/buzzer
│   └── config.h                 # Pins, polarity, thresholds, PIR disabled
├── bridge/
│   ├── protocol.py              # Validate serial readings / field mapping
│   └── runner.py        # CSV logging, ThingSpeak, Telegram
├── tests/testprotocol.py      # Offline automated Python tests
├── docs/                       # Guides (readable filenames use spaces)
├── assets/                     # Wiring and system architecture diagrams
├── .env.example                # Safe settings template
├── .gitignore                  # Excludes credentials and local data
├── platformio.ini              # VS Code PlatformIO project
├── requirements.txt
└── README.md
```

## Build milestones

- [ ] Verify each physical module's exact pin labels and voltage
- [ ] Upload Arduino firmware and obtain valid `DATA` lines
- [ ] Test DHT, light, sound and reed separately
- [ ] Verify the button and RGB/buzzer polarities
- [ ] Record at least 10 observations per sensor
- [ ] Adjust thresholds from measurements
- [ ] Verify ThingSpeak and Telegram using your actual accounts
- [ ] Test connectivity loss while local alarm still works
- [ ] Photograph assembly, Serial Monitor and dashboards
- [ ] Run final demonstration twice
- [ ] Next week only: install PIR at D7 and enable after verifying hardware

Start here: [complete step-by-step build guide](docs/02%20Complete%20Build%20Guide.md).

## Naming convention

Human-readable file and folder names use **spaces** rather than hyphens or underscores (for example, `room304 smart classroom iot`, `01 Wiring and Safety.md` and `pin map.svg`). Certain names that software expects must keep their fixed spelling, such as `.gitignore`, `.env.example`, `AGENTS.md`, `README.md`, `platformio.ini`, `config.h` and Python identifiers. The Arduino sketch is `Room304.ino` in its matching `Room304` folder because Arduino sketch names cannot include spaces. GitHub repository names also cannot contain spaces: if you need an all-letter name, use `room304smartclassroomiot`. If you already created a different GitHub repository, do not change the remote automatically.

## Safety / privacy

Low-voltage prototype only. Do not wire classroom mains lighting, AC, HVAC or actual building equipment. Do not record audio: this project measures a crude sound activity span, not speech content. Keep credentials and live logs out of GitHub. Check university and team permissions before publishing shared work.

## Technical references

- [Arduino IDE](https://www.arduino.cc/en/software)
- [PlatformIO UNO board](https://docs.platformio.org/page/boards/atmelavr/uno.html)
- [ThingSpeak Write Data](https://www.mathworks.com/help/thingspeak/writedata.html)
- [Telegram Bot API](https://core.telegram.org/bots/api)
