# Setup and operation

## Software prerequisites

- Python 3.10+, `pip` and VS Code or another editor
- PlatformIO (UNO environment in `platformio.ini`), including the DHT sensor libraries specified there
- Arduino UNO on a known serial port (`COM3` is only an example)
- ThingSpeak channel with eight fields for optional cloud uploads

From the repository root:

```powershell
python -m pip install -r requirements.txt -r dashboard/requirements.txt
Copy-Item .env.example .env
```

In `.env`, set `ROOM304_PORT` to the actual UNO port and retain `ROOM304_BAUD=9600`. For uploads, set `THINGSPEAK_WRITE_KEY` privately. For a local website, use `DASHBOARD_DATA_SOURCE=local`. Keep `.env` untracked.

## Firmware

The PlatformIO project lives in the repository root; `src_dir=firmware/Room304`. Build and upload to the UNO using PlatformIO. Serial Monitor at 9600 baud displays informational lines and periodic `DATA` records. **Only one process can open the serial port at a time.**

## Laptop bridge

Close Serial Monitor; then run:

```powershell
python -m bridge.runner
```

The bridge parses `DATA` lines, writes timestamped records to `data/logs/room304 readings.csv`, and—if configured—uploads to ThingSpeak approximately every 20 seconds. The terminal reports individual readings and upload success/failures. The bridge must stay running to upload new measurements.

## Local dashboard

In a second terminal:

```powershell
python -m dashboard.app
```

Open `http://127.0.0.1:5000`. Local mode reads the local CSV. The hosted Render site reads ThingSpeak; it does not need the local Flask process.

## Typical troubleshooting

| Observation | Check |
|:--|:--|
| COM port permission or access denied | Close PlatformIO Serial Monitor and other serial tools |
| No normal `DATA` lines | Confirm the Smart Classroom firmware, 9600 baud and selected UNO |
| Bridge reads sensors but cloud is stale | Confirm internet, private write key, upload success and channel ID |
| Hosted page has old readings | Confirm bridge is running; ThingSpeak freshness, Render credentials and matching channel |
| Login prompt appears | Use the credentials configured in the Render service, not GitHub credentials |
| Sound stays near 2–5 even during loud noise | Verify AO-to-A1 connection and signal amplitude before lowering thresholds |
| PIR remains HIGH | Allow warm-up and output hold time; test after it returns LOW |
| Door state fixed | Check reed magnet alignment and `REED_CLOSED_IS_LOW` |

## Verification

```powershell
python -m unittest discover -s tests -v
```

Tests are offline checks; physical calibration follows [Calibration and Verification](04%20Calibration%20and%20Verification.md).
