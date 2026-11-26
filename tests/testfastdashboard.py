"""Focused regression checks for low-latency dashboard (no hardware/network)."""
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone

from dashboard import app as dashboard


class FastCloudTests(unittest.TestCase):
    def setUp(self):
        dashboard._cloud_cache['data'] = None
        dashboard._cloud_recent_cache['data'] = None

    def _reply(self):
        reply = MagicMock()
        reply.json.return_value = {
            'channel': {'name': 'Room 304'},
            'feeds': [{'created_at': datetime.now(timezone.utc).isoformat(),
                       'field1': '21.7', 'field2': '32', 'field3': '635',
                       'field4': '2', 'field5': '1', 'field6': '0',
                       'field7': '0', 'field8': '1'}]
        }
        return reply

    def test_recent_overview_requests_only_160_from_thingspeak(self):
        with patch.dict('os.environ', {'DASHBOARD_DATA_SOURCE': 'cloud',
                                        'THINGSPEAK_CHANNEL_ID': '123456',
                                        'THINGSPEAK_READ_KEY': 'test-read-key',
                                        'DASHBOARD_REQUIRE_AUTH': 'false',
                                        'DASHBOARD_ACCESS_USERNAME': '',
                                        'DASHBOARD_ACCESS_PASSWORD': ''}), \
             patch('requests.get', return_value=self._reply()) as fetch:
            response = dashboard.app.test_client().get('/api/live?recent=1')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json['latest']['pir_motion'], 1)
            self.assertEqual(response.json['source'], 'cloud')
            self.assertEqual(fetch.call_args.kwargs['params']['results'], 160)
            self.assertEqual(response.headers['Cache-Control'], 'no-store')

    def test_full_history_still_requests_800(self):
        with patch.dict('os.environ', {'DASHBOARD_DATA_SOURCE': 'cloud',
                                        'THINGSPEAK_CHANNEL_ID': '123456',
                                        'THINGSPEAK_READ_KEY': 'test-read-key',
                                        'DASHBOARD_REQUIRE_AUTH': 'false',
                                        'DASHBOARD_ACCESS_USERNAME': '',
                                        'DASHBOARD_ACCESS_PASSWORD': ''}), \
             patch('requests.get', return_value=self._reply()) as fetch:
            response = dashboard.app.test_client().get('/api/live')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(fetch.call_args.kwargs['params']['results'], 800)

    def test_pir_and_private_account_features_still_in_html(self):
        with patch.dict('os.environ', {'DASHBOARD_REQUIRE_AUTH':'false',
                                        'DASHBOARD_ACCESS_USERNAME':'',
                                        'DASHBOARD_ACCESS_PASSWORD':''}):
            page = dashboard.app.test_client().get('/').get_data(as_text=True)
            self.assertIn('PIR motion, D7', page)
            self.assertNotIn('PIR, D7 (not installed)', page)
            self.assertIn('userMenuButton', page)
            self.assertIn('/api/live?recent=1', page)
            self.assertIn("CONFIG.fullUrl", page)


if __name__ == '__main__':
    unittest.main()
