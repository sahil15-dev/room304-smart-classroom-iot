"""Smart Classroom Sentinel dashboard: local CSV or private ThingSpeak history.

Local:  python -m dashboard.app             (DASHBOARD_DATA_SOURCE=local)
Hosted: gunicorn dashboard.app:app       (DASHBOARD_DATA_SOURCE=cloud)
The website NEVER opens Arduino serial or writes ThingSpeak data.
"""
from __future__ import annotations

from collections import deque
import csv
from datetime import datetime, timezone
import hmac
import io
import os
from pathlib import Path
import threading
import time

from flask import Flask, abort, jsonify, make_response, render_template, request, send_file

ROOT = Path(__file__).resolve().parents[1]
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / '.env', override=False)
except ImportError:
    pass

app = Flask(__name__)
LOG_PATH = ROOT / 'data' / 'logs' / 'room304 readings.csv'
FIELDS = ('temperature_c', 'humidity_percent', 'light', 'sound_span',
          'door_open', 'expected_empty', 'alert_code', 'pir_motion')
FIELDNAMES = ('timestamp_utc',) + FIELDS
_cloud_cache: dict = {'fetched': 0.0, 'data': None, 'channel': None}
_cloud_lock = threading.Lock()


def data_source() -> str:
    source = os.getenv('DASHBOARD_DATA_SOURCE', 'local').strip().lower()
    if source not in ('local', 'cloud'):
        raise ValueError('DASHBOARD_DATA_SOURCE must be local or cloud')
    return source


@app.before_request
def optional_password_gate():
    """Restrict sensor pages and APIs with HTTP Basic authentication.

    In hosted mode DASHBOARD_REQUIRE_AUTH=true fails closed if either
    credential is missing. Local development needs no login by default.
    """
    if request.path == '/api/health':
        # Non-sensitive endpoint for the hosting provider's health checks.
        return None

    username = os.getenv('DASHBOARD_ACCESS_USERNAME', '').strip()
    password = os.getenv('DASHBOARD_ACCESS_PASSWORD', '')
    mandatory = os.getenv('DASHBOARD_REQUIRE_AUTH', '').strip().lower() in ('1', 'true', 'yes')

    if mandatory and (not username or not password):
        return make_response(('Private dashboard credentials are not configured.', 503,
                              {'Cache-Control': 'no-store'}))
    if not password and not username:
        return None  # Local development only. Render sets REQUIRE_AUTH=true.
    if not password:
        return make_response(('Dashboard password is not configured.', 503,
                              {'Cache-Control': 'no-store'}))

    # Backwards compatibility for a local password-only setup. The deployed
    # Render service must have both variables explicitly configured.
    expected_username = username or 'viewer'
    authorization = request.authorization
    received_username = authorization.username if authorization else ''
    received_password = authorization.password if authorization else ''
    correct_username = hmac.compare_digest(received_username or '', expected_username)
    correct_password = hmac.compare_digest(received_password or '', password)
    if not (correct_username and correct_password):
        return make_response(('Dashboard login required', 401,
                              {'WWW-Authenticate': 'Basic realm="Smart Classroom Sentinel"',
                               'Cache-Control': 'no-store'}))
    return None


@app.after_request
def avoid_cached_sensor_data(response):
    if request.path.startswith('/api/'):
        response.headers['Cache-Control'] = 'no-store'
    return response


def parse_row(row: dict) -> dict:
    parsed = {'timestamp_utc': row.get('timestamp_utc', '')}
    for key in FIELDS:
        raw = row.get(key, '')
        try:
            val = float(raw)
            parsed[key] = None if val != val or abs(val) == float('inf') else (
                val if key in ('temperature_c', 'humidity_percent') else int(val))
        except (ValueError, TypeError):
            parsed[key] = None
    return parsed


def recent_readings(limit: int = 800) -> list[dict]:
    if not LOG_PATH.is_file():
        return []
    try:
        with LOG_PATH.open('r', newline='', encoding='utf-8') as source:
            return [parse_row(row) for row in deque(csv.DictReader(source), maxlen=limit)]
    except (OSError, UnicodeError, csv.Error):
        return []


def age_seconds(entry: dict) -> float | None:
    try:
        parsed = datetime.fromisoformat(entry['timestamp_utc'].replace('Z', '+00:00'))
        if parsed.tzinfo is None:
            # Bridge records UTC; treat naive timestamps as UTC, not Render's timezone.
            parsed = parsed.replace(tzinfo=timezone.utc)
        delta = (datetime.now(timezone.utc) - parsed).total_seconds()
        if delta < -5:
            return None  # Future timestamps must not create a false 'live' badge.
        return max(0., delta)
    except (ValueError, TypeError, KeyError, AttributeError):
        return None


def build_events(history: list[dict], limit: int = 8) -> list[dict]:
    events = []
    for prev, curr in zip(history, history[1:]):
        for field, label in (('expected_empty', 'Mode'), ('alert_code', 'Alert'), ('door_open', 'Door')):
            old, new = prev.get(field), curr.get(field)
            if old is None or new is None or old == new:
                continue
            if field == 'expected_empty':
                message = 'Expected-empty monitoring enabled' if new == 1 else 'Expected-occupied monitoring enabled'
                tone = 'neutral'
            elif field == 'door_open':
                message = 'Door input reports open' if new == 1 else 'Door input reports closed'
                tone = 'neutral'
            else:
                message = {0:'Conditions returned to normal', 1:'Comfort warning',
                           2:'Possible lighting waste', 3:'DHT sensor reading fault'}.get(new, f'Alert code {new}')
                tone = 'warn' if new in (1,2,3) else 'good'
            events.append({'timestamp_utc': curr.get('timestamp_utc',''),
                           'kind': label, 'message': message, 'tone': tone})
    return events[-limit:][::-1]


def cloud_feed(force: bool = False) -> dict:
    """Read ONLY: server-side ThingSpeak Read API key never reaches the browser."""
    channel_id = os.getenv('THINGSPEAK_CHANNEL_ID', '').strip()
    read_key = os.getenv('THINGSPEAK_READ_KEY', '').strip()
    if not channel_id:
        return {'configured': False, 'feeds': [], 'message': 'Configure THINGSPEAK_CHANNEL_ID on the server.'}
    if not channel_id.isdecimal():
        return {'configured': False, 'feeds': [], 'message': 'Channel ID must be numeric.'}
    with _cloud_lock:
        if (not force and _cloud_cache['data'] is not None
                and _cloud_cache['channel'] == channel_id
                and time.monotonic() - _cloud_cache['fetched'] < 25):
            return _cloud_cache['data']
    try:
        import requests
        params = {'results': 800}  # Supports the 480-row history view.
        if read_key:
            params['api_key'] = read_key
        response = requests.get(f'https://api.thingspeak.com/channels/{channel_id}/feeds.json',
                                params=params, timeout=10)
        response.raise_for_status()
        payload = response.json()
        feeds = []
        for entry in payload.get('feeds', []):
            row = {'timestamp_utc': entry.get('created_at', '')}
            for i, name in enumerate(FIELDS, start=1):
                row[name] = entry.get(f'field{i}')
            feeds.append(parse_row(row))
        result = {'configured': True, 'feeds': feeds, 'message': 'Cloud history connected',
                  'channel_name': payload.get('channel', {}).get('name', 'ThingSpeak')}
    except Exception:
        # Do not expose URLs or exceptions that might contain API keys.
        result = {'configured': True, 'feeds': [],
                  'message': 'Cloud feed unavailable. Verify the Channel ID, private Read key and internet.'}
    with _cloud_lock:
        _cloud_cache.update(fetched=time.monotonic(), data=result, channel=channel_id)
    return result


@app.get('/')
def index():
    return render_template('index.html')


@app.get('/api/me')
def current_user():
    """Return the identity verified by HTTP Basic auth; never return secrets.

    before_request has already authenticated hosted requests. An open local
    dashboard has no verified login, so it is explicitly labeled Local access.
    """
    username = os.getenv('DASHBOARD_ACCESS_USERNAME', '').strip()
    password = os.getenv('DASHBOARD_ACCESS_PASSWORD', '')
    if username or password:
        return jsonify({'username': username or 'viewer', 'authenticated': True})
    return jsonify({'username': 'Local access', 'authenticated': False})


@app.get('/api/live')
def live():
    source = data_source()
    if source == 'cloud':
        cloud = cloud_feed()
        history = cloud['feeds']
        message = cloud['message']
    else:
        history = recent_readings()
        message = 'Local CSV from the USB Python bridge'
    latest = history[-1] if history else None
    age = age_seconds(latest) if latest else None
    # ThingSpeak updates ~20s, plus API cache. Allow normal cloud delays.
    window = 90 if source == 'cloud' else 20
    return jsonify({'source': source, 'latest': latest, 'history': history,
                    'age_seconds': round(age,1) if age is not None else None,
                    'connected': age is not None and age < window,
                    'row_count': len(history), 'events': build_events(history),
                    'message': message})


@app.get('/api/cloud')
def cloud():
    return jsonify(cloud_feed(force=request.args.get('refresh') == '1'))


def csv_bytes(readings: list[dict]) -> bytes:
    buffer = io.StringIO(newline='')
    writer = csv.DictWriter(buffer, fieldnames=FIELDNAMES, extrasaction='ignore')
    writer.writeheader()
    writer.writerows(readings)
    return buffer.getvalue().encode('utf-8-sig')


@app.get('/api/export.csv')
def export_csv():
    if data_source() == 'cloud':
        rows = cloud_feed()['feeds']
        if not rows:
            abort(404, description='Cloud readings not available')
        return send_file(io.BytesIO(csv_bytes(rows)), as_attachment=True,
                         download_name='room304 available cloud readings.csv', mimetype='text/csv')
    if not LOG_PATH.is_file():
        abort(404, description='No local readings available yet')
    return send_file(LOG_PATH, as_attachment=True, download_name='room304 readings.csv',
                     mimetype='text/csv', conditional=True)


@app.get('/api/health')
def health():
    return jsonify({'ok': True, 'service': 'Smart Classroom Sentinel'})


if __name__ == '__main__':
    bind = os.getenv('DASHBOARD_BIND', '127.0.0.1')
    if bind not in ('127.0.0.1', '0.0.0.0'):
        raise ValueError('DASHBOARD_BIND must be 127.0.0.1 or 0.0.0.0')
    port = int(os.getenv('DASHBOARD_PORT', '5000'))
    print(f'Room 304 dashboard: http://127.0.0.1:{port} ({data_source()} mode)')
    app.run(host=bind, port=port, debug=False)
