"""Room 304 local and hosted dashboard regression tests.

Run from the existing project root with Flask installed:
    python -m unittest discover -s tests -v

These tests use the Flask test client and never require ThingSpeak or hardware.
"""
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from dashboard import app as dashboard

HEADER = ('timestamp_utc,temperature_c,humidity_percent,light,sound_span,'
          'door_open,expected_empty,alert_code,pir_motion\n')


class DashboardTests(unittest.TestCase):
    def test_website_has_reference_sections_and_scroll_regions(self):
        response = dashboard.app.test_client().get('/')
        self.assertEqual(response.status_code, 200)
        markup = response.data
        for marker in (b'Test &amp; calibrate', b'Data history', b'id="plan"',
                       b'id="tests"', b'id="rowSel"', b'class="tbl-wrap"',
                       b'max-height:min(69vh,760px)', b'height:min(60vh,650px)',
                       b'/api/live', b'/api/cloud', b'/api/export.csv'):
            self.assertIn(marker, markup)
        # The browser must not silently substitute fabricated sensor values.
        self.assertNotIn(b'demoFallback: true', markup)
        # Keys are private .env values, not configurable in this HTML.
        self.assertNotIn(b'readApiKey:', markup)

    def test_no_logs_shows_waiting_not_simulated_values(self):
        with patch.object(dashboard, 'LOG_PATH', Path('/nonexistent/room304/hello.csv')):
            client = dashboard.app.test_client()
            payload = client.get('/api/live').get_json()
            self.assertFalse(payload['connected'])
            self.assertIsNone(payload['latest'])
            self.assertEqual(payload['history'], [])
            self.assertEqual(payload['events'], [])
            self.assertEqual(client.get('/api/export.csv').status_code, 404)

    def test_readings_include_all_real_fields_and_export_full_csv(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'readings.csv'
            # Build a genuinely historical fixture regardless of local timezone
            # or the day/time at which the tests are executed.
            old_time = datetime.now(timezone.utc) - timedelta(hours=2)
            t1 = old_time.isoformat(timespec='seconds')
            t2 = (old_time + timedelta(seconds=3)).isoformat(timespec='seconds')
            path.write_text(HEADER +
                f'{t1},21.3,27.0,789,8,1,0,0,0\n'
                f'{t2},21.4,26.0,770,19,0,1,1,0\n',
                encoding='utf-8')
            with patch.object(dashboard, 'LOG_PATH', path):
                client = dashboard.app.test_client()
                data = client.get('/api/live').get_json()
                self.assertEqual(data['latest']['temperature_c'], 21.4)
                self.assertEqual(data['latest']['light'], 770)
                self.assertEqual(data['latest']['sound_span'], 19)
                self.assertEqual(data['latest']['pir_motion'], 0)
                self.assertFalse(data['connected'])  # Historical timestamps, not live.
                self.assertEqual(len(data['events']), 3)
                exported = client.get('/api/export.csv')
                try:
                    self.assertEqual(exported.status_code, 200)
                    self.assertIn(t1.encode(), exported.data)
                    self.assertIn(t2.encode(), exported.data)
                    self.assertIn('attachment', exported.headers['Content-Disposition'])
                finally:
                    # Werkzeug may stream from an open file. Close the response
                    # before TemporaryDirectory removes readings.csv on Windows.
                    exported.close()

    def test_future_timestamp_cannot_claim_live_connection(self):
        future = datetime.now(timezone.utc) + timedelta(hours=1)
        self.assertIsNone(dashboard.age_seconds({'timestamp_utc': future.isoformat()}))

    def test_scroll_history_can_request_more_than_480_samples(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'large.csv'
            lines = [f'2026-11-23T12:00:{i%60:02d}+00:00,24.0,40,800,5,1,0,0,0\n'
                     for i in range(620)]
            path.write_text(HEADER + ''.join(lines), encoding='utf-8')
            with patch.object(dashboard, 'LOG_PATH', path):
                result = dashboard.app.test_client().get('/api/live').get_json()
                self.assertEqual(len(result['history']), 620)
                self.assertEqual(result['row_count'], 620)

    def test_transitions_are_observations_not_controls(self):
        events = dashboard.build_events([
            {'timestamp_utc': 'first', 'expected_empty': 0, 'door_open': 1, 'alert_code': 0},
            {'timestamp_utc': 'second', 'expected_empty': 1, 'door_open': 0, 'alert_code': 2},
        ])
        self.assertEqual(len(events), 3)
        self.assertEqual(events[0]['kind'], 'Door')
        self.assertTrue(any(e['message'] == 'Possible lighting waste' for e in events))

    def test_cloud_mode_uses_private_read_feed_not_local_csv(self):
        from unittest.mock import MagicMock
        now = datetime.now(timezone.utc).isoformat()
        fake_reply = MagicMock()
        fake_reply.json.return_value = {
            'channel': {'name': 'Room 304 Smart Classroom'},
            'feeds': [{'created_at': now, 'field1': '22.0', 'field2': '45.0',
                       'field3': '720', 'field4': '16', 'field5': '1',
                       'field6': '0', 'field7': '0', 'field8': '0'}]
        }
        with patch.dict('os.environ', {'DASHBOARD_DATA_SOURCE': 'cloud',
                                        'THINGSPEAK_CHANNEL_ID': '123456',
                                        'THINGSPEAK_READ_KEY': 'private-read-key',
                                        'DASHBOARD_ACCESS_PASSWORD': ''}), \
             patch('requests.get', return_value=fake_reply) as request_mock:
            dashboard._cloud_cache['data'] = None
            client = dashboard.app.test_client()
            payload = client.get('/api/live').get_json()
            self.assertEqual(payload['source'], 'cloud')
            self.assertEqual(payload['latest']['temperature_c'], 22.0)
            self.assertTrue(payload['connected'])
            self.assertNotIn('private-read-key', str(payload))
            self.assertEqual(client.get('/api/export.csv').status_code, 200)
            args, kwargs = request_mock.call_args
            self.assertIn('api.thingspeak.com', args[0])
            self.assertEqual(kwargs['params']['api_key'], 'private-read-key')
            self.assertEqual(kwargs['params']['results'], 800)

    def test_cloud_mode_historical_data_is_not_live(self):
        with patch.dict('os.environ', {'DASHBOARD_DATA_SOURCE': 'cloud',
                                       'DASHBOARD_ACCESS_PASSWORD': ''}), \
             patch.object(dashboard, 'cloud_feed', return_value={
                 'configured': True, 'feeds': [{
                    'timestamp_utc': '2020-01-01T00:00:00Z',
                    'temperature_c': 22.0, 'humidity_percent': 42.0,
                    'light': 760, 'sound_span': 4, 'door_open': 1,
                    'expected_empty': 0, 'alert_code': 0, 'pir_motion': 0}],
                 'message': 'Cloud history connected'}):
            data = dashboard.app.test_client().get('/api/live').get_json()
            self.assertFalse(data['connected'])
            self.assertEqual(data['source'], 'cloud')
            self.assertGreater(data['age_seconds'], 86400)

    def test_optional_password_protects_the_sensor_api(self):
        import base64
        with patch.dict('os.environ', {'DASHBOARD_ACCESS_PASSWORD': 'my-test-password',
                                       'DASHBOARD_DATA_SOURCE': 'local'}):
            client = dashboard.app.test_client()
            self.assertEqual(client.get('/').status_code, 401)
            self.assertEqual(client.get('/api/live').status_code, 401)
            self.assertEqual(client.get('/api/health').status_code, 200)
            token = base64.b64encode(b'viewer:my-test-password').decode()
            res = client.get('/api/live', headers={'Authorization': 'Basic ' + token})
            self.assertEqual(res.status_code, 200)

    def test_cloud_feed_displays_failure_without_exposing_key(self):
        with patch.dict('os.environ', {'THINGSPEAK_CHANNEL_ID': '9999',
                                       'THINGSPEAK_READ_KEY': 'sensitive-secret',
                                       'DASHBOARD_ACCESS_PASSWORD': ''}), \
             patch('requests.get', side_effect=Exception('bad url sensitive-secret')):
            result = dashboard.cloud_feed(force=True)
            self.assertEqual(result['feeds'], [])
            self.assertNotIn('sensitive-secret', result['message'])

    def test_unconfigured_cloud_does_not_require_secret(self):
        with patch.dict('os.environ', {'THINGSPEAK_CHANNEL_ID': ''}):
            payload = dashboard.app.test_client().get('/api/cloud').get_json()
            self.assertFalse(payload['configured'])
            self.assertEqual(payload['feeds'], [])


if __name__ == '__main__':
    unittest.main()
