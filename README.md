<p align="center">
  <img src="assets/project%20banner.png" alt="Smart Classroom Sentinel - Room 304" width="100%" />
</p>

# Smart Classroom Sentinel

**Room 304 · Embedded SW & IoT · Arduino UNO + Python + ThingSpeak + Flask**

A local-first, low-voltage classroom monitoring prototype. Sensor readings are interpreted by an Arduino UNO, logged by a laptop Python bridge, stored in a private ThingSpeak channel and displayed on a read-only web dashboard. The physical RGB LED and buzzer provide local warnings even when the laptop is offline. **No Telegram, Discord, remote mains switching or live audio recordings are required.**

> **Project state · 23 November 2026:** The USB sensor stream, laptop Python bridge, ThingSpeak updates and local website have been demonstrated. The Mini Reed magnet test, final microphone and light thresholds, and physical LED/buzzer sign-off are still pending the classroom session. PIR is *not installed*; Arduino D7 is reserved and disabled. A hosted Render dashboard is prepared but **has not yet been deployed**.

<p align="center"><img src="assets/dashboard%20preview.png" alt="Screenshot of the working local dashboard" width="94%" /></p>
<p align="center"><i>Development screenshot from real browser testing; numbers are historical and not a live feed inside this README.</i></p>

## How it works

![Project architecture](assets/system%20architecture.png)

**Hardware:** DHT11 for indoor temperature/humidity; photoresistor for relative brightness; Big Sound module for relative sound activity; Mini Reed for door state; a pushbutton for the *expected-empty* mode; RGB LED and buzzer for warnings. The microphone outputs a numeric activity span, **not recorded speech or decibels**. The button's expected-empty setting **does not verify physical occupancy**.

**Laptop:** The Arduino sends `DATA,temp,humidity,light,sound_span,door_open,expected_empty,alert,pir` at 9600 baud. `bridge/runner.py` owns the serial port, writes `data/logs/room304 readings.csv` and optionally uploads to ThingSpeak every ~20 seconds.

**Website:** `dashboard/app.py` serves the same polished website in two modes. `local` reads the laptop CSV, while `cloud` reads ThingSpeak *server-side* and supports deployment on Render. Neither mode sends commands back to the Arduino. The public URL can stay reachable without your laptop, but **new measurements require the Arduino + laptop bridge to be running**.

## Verified and pending

| Component | Status as of 23 Nov 2026 |
| :-- | :-- |
| Arduino UNO / PlatformIO | Firmware uploaded and emits structured serial readings |
| Temperature and humidity | Actual readings visible; precision not independently verified |
| Photoresistor | Responsive, **lower ADC = brighter**; final threshold needs classroom calibration |
| Microphone | Numeric sound span visible; loud/quiet separation needs final measurement |
| Mode button | `expected_empty` toggles 0 ↔ 1 in real serial data |
| Python bridge / ThingSpeak | Confirmed working and sending recent points |
| Local Flask website | Confirmed displaying actual sensor data and cloud history |
| Mini Reed | Magnet confirmation pending |
| RGB LED / buzzer | Physical behavior not fully signed off |
| Hosted website | Deployment package ready; **not yet live** |
| PIR on D7 | **Disabled, planned upgrade** |

## Run the system locally

Keep the existing VS Code project; do not create a second PlatformIO project. With Arduino connected and PlatformIO Serial Monitor **closed**:

```powershell
python -m pip install -r requirements.txt -r dashboard/requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
# Enter your COM port and private ThingSpeak keys in local .env.
python -m unittest discover -s tests -v
```

**Terminal 1** — the only process that opens COM3 (or your actual USB port):

```powershell
python -m bridge.runner
```

**Terminal 2** — website, using the same private `.env`:

```powershell
python -m dashboard.app
```

Open **http://127.0.0.1:5000**. Set `DASHBOARD_DATA_SOURCE=local` in `.env` for live laptop CSV readings. A stale/offline badge means the logged data is old; the website does not invent measurements. See [Local web guide](docs/07%20Local%20Web%20Dashboard.md).

## Put the website online and auto-update from GitHub

![Deployment modes](assets/deployment%20architecture.png)

This repository includes **`render.yaml`** for a **read-only hosted Flask service** that uses your private ThingSpeak **Read API Key**. The same site is displayed online, and pushing to the connected GitHub branch can automatically redeploy it. The Render service does **not** run the USB Python bridge. The existing local dashboard and offline Arduino alarms are unchanged.

1. Push this repository to your existing private GitHub repo (do not commit `.env`).
2. At [Render](https://dashboard.render.com/), create a new **Blueprint** from that specific GitHub repository, which picks up `render.yaml`.
3. Supply **`THINGSPEAK_CHANNEL_ID`** and **`THINGSPEAK_READ_KEY`** as Render environment variables—not GitHub files. `DASHBOARD_DATA_SOURCE=cloud` is configured automatically.
4. Optionally add `DASHBOARD_ACCESS_PASSWORD` on Render to restrict the website with a browser password prompt.
5. After the deployment succeeds, add the real `https://....onrender.com` URL to the repository's **About → Website** field and replace the placeholder in [Online Deployment](docs/11%20Online%20Deployment.md).

> Free Render instances may sleep after inactivity and wake on a new visit. For strict *always-on* access, choose an appropriate paid plan. Cloud history remains visible when the laptop is offline but will be **stale** until the bridge uploads again. Hosted downloads include *available cloud samples*, while local mode exports the complete local CSV.

**Full deployment instructions:** [11 Online Deployment](docs/11%20Online%20Deployment.md).

## Hardware and software details

![Pin assignments](assets/pin%20map.png)

| UNO input/output | Function |
| :-- | :-- |
| D2 | DHT11 data |
| D3 | Mini Reed signal |
| D4 | Mode button signal |
| D5 | Active buzzer |
| D6 / D9 / D10 | RGB red / green / blue |
| D7 | Reserved PIR, **disabled** |
| A0 | Photoresistor analog signal |
| A1 | Big Sound **AO** (not DO) |

All compatible modules share rated 5V and common GND. A bare RGB LED requires separate current-limiting resistors. Verify each actual sensor module's pin labels before wiring. **Never connect to classroom mains, HVAC or building lighting circuits.**

![Alert reference](assets/alert%20reference.png)

## Repository map

```text
room304 smart classroom iot/
├── assets/                       # Editable SVGs, PNG previews and dashboard screenshot
├── bridge/                       # Arduino serial -> validation -> CSV -> ThingSpeak
├── dashboard/                    # Flask website, HTML, optional Dockerfile
├── docs/                         # Wiring, test plan, deployment and handoff
├── firmware/Room304/             # PlatformIO Arduino sketch and config
├── tests/                        # Offline Python regression tests
├── .github/workflows/verify.yml  # CI tests on pushes and pull requests
├── .env.example                  # Placeholder values only; no real keys
├── .gitignore                    # Ignores .env, logs, local builds
├── platformio.ini
├── render.yaml                   # Optional cloud deployment with auto-deploy
├── requirements.txt
└── README.md
```

## Testing and presentation evidence

The **Test & Calibrate** page provides a manual checklist and notes. **Data History** supports scrolling and export. Save real classroom photographs, sensor threshold measurements, a test report and ThingSpeak screenshots to your local evidence folder; publish only sanitized, permission-approved screenshots. The included GitHub Actions workflow runs offline Python tests but **does not count as physical validation**.

- [Wiring and safety](docs/01%20Wiring%20and%20Safety.md) · [Complete build](docs/02%20Complete%20Build%20Guide.md) · [Cloud fields and alerts](docs/03%20Cloud%20and%20Alerts.md)
- [Test plan](docs/04%20Test%20Plan%20and%20Results.md) · [Progress](docs/05%20Progress%20and%20Next%20Steps.md) · [Repository handoff](docs/12%20Repository%20Handoff.md)

**Privacy and scope:** Keep `.env` and live logs out of source control. A publicly accessible hosted dashboard exposes the *displayed room data*, even if the ThingSpeak channel itself is private; use `DASHBOARD_ACCESS_PASSWORD` if needed and obtain permission before showing classroom data publicly. A live website is a monitoring view, not a remote controller or verified occupancy detector.
