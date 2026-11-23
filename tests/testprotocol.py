"""Run: python -m unittest discover -s tests -v"""
import tempfile
from pathlib import Path
from unittest.mock import patch
import unittest

from bridge.protocol import parse_serial_line, thingspeak_fields, alert_message
from bridge.runner import Monitor


class ProtocolTests(unittest.TestCase):
    def test_valid_reading(self):
        r = parse_serial_line('DATA,24.0,53.5,750,32,1,0,0,0')
        self.assertIsNotNone(r)
        self.assertEqual(r.temperature_c, 24.0)
        self.assertEqual(r.light, 750)
        self.assertEqual(r.pir_motion, 0)

    def test_ignores_info(self):
        self.assertIsNone(parse_serial_line('INFO,Room304 ready'))

    def test_rejects_missing_field(self):
        self.assertIsNone(parse_serial_line('DATA,24,55,3,4,0,0,0'))

    def test_rejects_invalid_binary_value(self):
        self.assertIsNone(parse_serial_line('DATA,24,55,300,5,8,0,0,0'))

    def test_rejects_out_of_range_analog(self):
        self.assertIsNone(parse_serial_line('DATA,24,55,9999,5,0,0,0,0'))

    def test_dht_error_permits_nan(self):
        r = parse_serial_line('DATA,nan,nan,400,6,0,0,3,0')
        self.assertIsNone(r.temperature_c)
        self.assertIsNone(r.humidity_percent)

    def test_nan_without_fault_is_invalid(self):
        self.assertIsNone(parse_serial_line('DATA,nan,nan,400,6,0,0,0,0'))

    def test_fields_mapping(self):
        r = parse_serial_line('DATA,24,50,800,40,1,1,2,0')
        fields = thingspeak_fields(r)
        self.assertEqual(fields['field1'], 24)
        self.assertEqual(fields['field8'], 0)
        self.assertEqual(len(fields), 8)

    def test_normal_alert_has_no_message(self):
        r = parse_serial_line('DATA,24,50,500,3,0,0,0,0')
        self.assertIsNone(alert_message(r))

    def test_alert_message_mentions_type(self):
        r = parse_serial_line('DATA,24,50,900,3,0,1,2,0')
        self.assertIn('unnecessary classroom lighting', alert_message(r))


    def test_discord_optional_no_config_no_calls(self):
        r = parse_serial_line('DATA,21.3,25.0,4,8,1,1,1,0')
        with tempfile.TemporaryDirectory() as tmp, patch('bridge.runner.post_discord') as send:
            Monitor(Path(tmp) / 'readings.csv').handle(r, now=0)
            send.assert_not_called()

    def test_discord_alert_transition_cooldown(self):
        warning = parse_serial_line('DATA,21.3,25.0,4,8,1,1,1,0')
        normal = parse_serial_line('DATA,21.3,50.0,4,8,1,1,0,0')
        with tempfile.TemporaryDirectory() as tmp, patch('bridge.runner.post_discord') as send:
            monitor = Monitor(Path(tmp) / 'readings.csv', discord_webhook='https://example.test/webhook')
            monitor.handle(warning, now=0)
            monitor.handle(warning, now=10)
            self.assertEqual(send.call_count, 1)
            monitor.handle(warning, now=301)
            self.assertEqual(send.call_count, 2)
            monitor.handle(normal, now=310)
            monitor.handle(warning, now=320)
            self.assertEqual(send.call_count, 3)

    def test_thingspeak_20s_upload_interval(self):
        reading = parse_serial_line('DATA,21.3,25.0,4,8,1,1,1,0')
        with tempfile.TemporaryDirectory() as tmp, patch('bridge.runner.post_thingspeak') as send:
            monitor = Monitor(Path(tmp) / 'readings.csv', write_key='fakekey')
            monitor.handle(reading, now=0)
            monitor.handle(reading, now=5)
            monitor.handle(reading, now=20)
            self.assertEqual(send.call_count, 2)

    def test_offline_log(self):
        r = parse_serial_line('DATA,24,50,900,3,0,1,2,0')
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'logs' / 'data.csv'
            monitor = Monitor(path)
            monitor.handle(r, offline=True)
            self.assertEqual(len(path.read_text().splitlines()), 2)
            self.assertIn('timestamp_utc', path.read_text())


if __name__ == '__main__':
    unittest.main()
