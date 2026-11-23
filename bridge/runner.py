"""USB Serial -> CSV logging -> optional ThingSpeak uploads.

Run: python -m bridge.runner
Demo (no hardware/network): python -m bridge.runner --simulate
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import os
from pathlib import Path
import sys
import time

from .protocol import Reading, alert_message, parse_serial_line, thingspeak_fields

ROOT = Path(__file__).resolve().parents[1]
LOG_HEADERS = ['timestamp_utc', 'temperature_c', 'humidity_percent', 'light',
               'sound_span', 'door_open', 'expected_empty', 'alert_code', 'pir_motion']


def load_settings() -> None:
    """Load .env for local use, without replacing explicitly set environment values."""
    env_path = ROOT / '.env'
    if not env_path.exists():
        return
    try:
        from dotenv import load_dotenv
    except ImportError:
        print('Install dependencies with: python -m pip install -r requirements.txt')
        return
    load_dotenv(env_path, override=False)


def append_log(reading: Reading, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not path.exists() or path.stat().st_size == 0
    with path.open('a', newline='', encoding='utf-8') as stream:
        writer = csv.writer(stream)
        if write_header:
            writer.writerow(LOG_HEADERS)
        writer.writerow([datetime.now(timezone.utc).isoformat(),
                         reading.temperature_c, reading.humidity_percent,
                         reading.light, reading.sound_span, reading.door_open,
                         reading.expected_empty, reading.alert_code, reading.pir_motion])


def post_thingspeak(reading: Reading, write_key: str) -> None:
    import requests
    payload = {'api_key': write_key, **thingspeak_fields(reading)}
    response = requests.post('https://api.thingspeak.com/update.json',
                             data=payload, timeout=12)
    response.raise_for_status()
    result = response.json()
    # ThingSpeak can return 0 for rejected writes (e.g., too frequent, invalid key).
    if result == 0 or result == '0' or result is None:
        raise ValueError('ThingSpeak rejected update (check key/interval)')
    print('ThingSpeak upload successful')


class Monitor:
    def __init__(self, log_path: Path, write_key: str = '',
                 cloud_interval_s: float = 20.0):
        self.log_path = log_path
        self.write_key = write_key
        self.cloud_interval_s = max(cloud_interval_s, 20.0)
        self.last_cloud_attempt = float('-inf')

    def handle(self, reading: Reading, now: float | None = None, offline: bool = False) -> None:
        now = time.monotonic() if now is None else now
        append_log(reading, self.log_path)
        print('Reading:', reading)
        if offline:
            return
        if self.write_key and now - self.last_cloud_attempt >= self.cloud_interval_s:
            self.last_cloud_attempt = now
            try:
                post_thingspeak(reading, self.write_key)
            except Exception as error:
                print('ThingSpeak failed:', type(error).__name__, str(error)[:140], file=sys.stderr)


def simulate() -> None:
    print('OFFLINE DEMO: no Arduino or ThingSpeak required.')
    monitor = Monitor(ROOT / 'data' / 'logs' / 'simulated readings.csv')
    for line in [
        'INFO,Room304 ready; PIR disabled',
        'DATA,24.0,52.0,250,13,0,0,0,0',
        'DATA,24.1,53.0,810,65,1,0,0,0',
        'DATA,29.5,53.0,800,15,0,0,1,0',
        'DATA,24.0,53.0,850,12,0,1,2,0',
        'DATA,nan,nan,850,12,0,1,3,0',
    ]:
        reading = parse_serial_line(line)
        if reading:
            monitor.handle(reading, offline=True)
    print('Demo CSV saved:', monitor.log_path)


def run_serial() -> int:
    load_settings()
    try:
        import serial
    except ImportError:
        print('Missing pyserial. Install: python -m pip install -r requirements.txt')
        return 2
    port = os.getenv('ROOM304_PORT', 'COM3')
    try:
        baud = int(os.getenv('ROOM304_BAUD', '9600'))
    except ValueError:
        print('ROOM304_BAUD must be an integer')
        return 2
    monitor = Monitor(ROOT / 'data' / 'logs' / 'room304 readings.csv',
                      os.getenv('THINGSPEAK_WRITE_KEY', '').strip())
    print(f'Connecting to Arduino on {port} at {baud} baud. Close Arduino Serial Monitor first.')
    try:
        with serial.Serial(port, baudrate=baud, timeout=3) as device:
            time.sleep(2)  # UNO often resets on USB serial connection.
            while True:
                raw = device.readline().decode('utf-8', errors='replace').strip()
                if raw.startswith('INFO,'):
                    print(raw)
                reading = parse_serial_line(raw)
                if reading:
                    monitor.handle(reading)
    except KeyboardInterrupt:
        print('\nStopped by user')
        return 0
    except serial.SerialException as error:
        print('Serial connection failed:', error)
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(description='Room304 USB sensor cloud bridge')
    parser.add_argument('--simulate', action='store_true', help='Offline sample data; no network or USB')
    arguments = parser.parse_args()
    if arguments.simulate:
        simulate()
        return 0
    return run_serial()


if __name__ == '__main__':
    raise SystemExit(main())
