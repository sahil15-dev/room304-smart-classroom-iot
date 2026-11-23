# Room 304 — Local Website Dashboard

The dashboard is **read-only**. Arduino mode is still changed using its physical button. The Python bridge is the only process that opens COM3; the dashboard only reads the bridge's CSV and (optionally) reads ThingSpeak over HTTPS.

## Install and run locally (recommended)

Copy `dashboard/` into your existing `room304 smart classroom iot` repository. Keep the current `bridge/` folder, Arduino firmware, and `.env` unchanged. From the project root in VS Code PowerShell:

```powershell
python -m pip install -r requirements.txt -r dashboard/requirements.txt
```

Check that `.env` has:

```ini
ROOM304_PORT=COM3
ROOM304_BAUD=9600
THINGSPEAK_WRITE_KEY=YOUR_PRIVATE_WRITE_KEY
THINGSPEAK_CHANNEL_ID=YOUR_NUMERIC_CHANNEL_ID
THINGSPEAK_READ_KEY=YOUR_PRIVATE_READ_KEY
```

Leave `DISCORD_WEBHOOK_URL` blank unless needed. For a **public** ThingSpeak channel, the Read key can be blank; we recommend keeping your channel **private**.

1. Stop PlatformIO Serial Monitor (`Ctrl+C`).
2. **Terminal 1:** `python -m bridge.runner` — owns COM3 and writes `data/logs/room304 readings.csv`; pushes updates to ThingSpeak.
3. **Terminal 2:** `python -m dashboard.app` — reads CSV and private ThingSpeak history; does **not** open COM3.
4. Visit **http://127.0.0.1:5000** on your laptop.

The website shows "Waiting for bridge" until the first actual reading has been logged. It labels local readings **stale** if the CSV is older than 20 seconds.

## Run website in Docker instead (optional)

Leave the USB bridge running **on Windows**. In PowerShell at project root:

```powershell
docker build -f dashboard/Dockerfile -t room304-dashboard .
docker run --rm --name room304-dashboard --env-file .env -p 127.0.0.1:5000:5000 -v "${PWD}/data/logs:/app/data/logs:ro" room304-dashboard
```

Docker Desktop must be running. Keep `.env` out of Git and out of the Docker image. Do not put your Arduino's COM3 connection into the dashboard container; only `bridge.runner` reads serial on the host.

## Security / limitations

- Binds to localhost by default. Avoid exposing this development dashboard to a public network.
- Neither Read nor Write API Keys are sent to browser scripts. Flask requests ThingSpeak on the server side.
- Only the Python bridge can write ThingSpeak data (using the Write API Key). The website reads cloud history (using Channel ID and Read API Key).
- **Read-only by design:** browser controls for changing Arduino mode would need an explicit command protocol in the firmware and bridge, authentication, and testing. The existing physical mode button works now.
- This app is for classroom demos, not a production authenticated internet service.
- CSV is read repeatedly; for long-term continuous data collection, migrate the dashboard to a database or add incremental log tailing.

## Saving changes to GitHub

```powershell
git add dashboard "docs/07 Local Web Dashboard.md"
git diff --cached --name-only
git commit -m "Add local Room 304 web dashboard"
git push
```

Do not commit `.env`, logs, or secret tokens.
