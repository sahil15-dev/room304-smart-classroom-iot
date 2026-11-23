"""Access-control tests for private Render deployment (no network required)."""
import base64
import unittest
from unittest.mock import patch
from dashboard import app as dashboard


def credentials(username, password):
    value = base64.b64encode(f'{username}:{password}'.encode('utf-8')).decode('ascii')
    return {'Authorization': f'Basic {value}'}


class PrivateDashboardTests(unittest.TestCase):
    def test_missing_hosted_credentials_fail_closed(self):
        with patch.dict('os.environ', {
            'DASHBOARD_REQUIRE_AUTH': 'true',
            'DASHBOARD_ACCESS_USERNAME': '',
            'DASHBOARD_ACCESS_PASSWORD': '',
        }):
            client = dashboard.app.test_client()
            for route in ('/', '/api/live', '/api/cloud', '/api/export.csv'):
                self.assertEqual(client.get(route).status_code, 503)
            self.assertEqual(client.get('/api/health').status_code, 200)

    def test_both_username_and_password_are_required(self):
        with patch.dict('os.environ', {
            'DASHBOARD_REQUIRE_AUTH': 'true',
            'DASHBOARD_ACCESS_USERNAME': 'private-viewer',
            'DASHBOARD_ACCESS_PASSWORD': 'long-test-password',
            'DASHBOARD_DATA_SOURCE': 'local',
        }):
            client = dashboard.app.test_client()
            for route in ('/', '/api/live', '/api/cloud', '/api/export.csv'):
                self.assertEqual(client.get(route).status_code, 401)
                self.assertEqual(client.get(route, headers=credentials('bad-name', 'long-test-password')).status_code, 401)
                self.assertEqual(client.get(route, headers=credentials('private-viewer', 'bad-password')).status_code, 401)
            self.assertEqual(client.get('/api/live', headers=credentials('private-viewer', 'long-test-password')).status_code, 200)

    def test_user_tab_requires_valid_login_and_shows_only_username(self):
        with patch.dict('os.environ', {
            'DASHBOARD_REQUIRE_AUTH': 'true',
            'DASHBOARD_ACCESS_USERNAME': 'classroom-owner',
            'DASHBOARD_ACCESS_PASSWORD': 'private-password-for-test',
        }):
            client = dashboard.app.test_client()
            self.assertEqual(client.get('/api/me').status_code, 401)
            self.assertEqual(client.get('/api/me', headers=credentials('wrong', 'private-password-for-test')).status_code, 401)
            resp = client.get('/api/me', headers=credentials('classroom-owner', 'private-password-for-test'))
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.json, {'username': 'classroom-owner', 'authenticated': True})
            self.assertNotIn('private-password-for-test', resp.get_data(as_text=True))

    def test_local_user_tab_is_labeled_unverified(self):
        with patch.dict('os.environ', {
            'DASHBOARD_REQUIRE_AUTH': 'false',
            'DASHBOARD_ACCESS_USERNAME': '',
            'DASHBOARD_ACCESS_PASSWORD': '',
        }):
            resp = dashboard.app.test_client().get('/api/me')
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.json, {'username': 'Local access', 'authenticated': False})

    def test_local_dashboard_stays_open_without_credentials(self):
        with patch.dict('os.environ', {
            'DASHBOARD_REQUIRE_AUTH': 'false',
            'DASHBOARD_ACCESS_USERNAME': '',
            'DASHBOARD_ACCESS_PASSWORD': '',
            'DASHBOARD_DATA_SOURCE': 'local',
        }):
            self.assertEqual(dashboard.app.test_client().get('/api/live').status_code, 200)


if __name__ == '__main__':
    unittest.main()
