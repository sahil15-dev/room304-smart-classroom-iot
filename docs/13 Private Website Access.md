# Private website access on Render

This update protects the hosted Smart Classroom Sentinel dashboard with both a username and a password using HTTPS + browser HTTP Basic Authentication.

## Protection boundaries

- The deployed Flask server requires a matching username **and** password to view the dashboard, sensor APIs and CSV export.
- The simple `/api/health` endpoint remains public for Render health checks but contains no sensor data.
- `DASHBOARD_REQUIRE_AUTH=true` makes cloud deployment **fail closed**: missing credentials produce HTTP 503, not an unprotected dashboard.
- Local `DASHBOARD_REQUIRE_AUTH=false` leaves localhost open unless credentials are explicitly configured.
- HTTP Basic is appropriate for a small private demo over Render HTTPS, not a full multi-user authentication system. There is no per-user auditing, login throttling, or account recovery. Use a long unique password and do not reuse a banking or email password.
- Credential protection does not stop all requests or internet traffic hitting a publicly reachable URL. It protects the dashboard and API content. For a larger production service, add a managed access gateway, rate limits and monitoring.

## Variables in Render (not GitHub)

In the Render Blueprint deployment, enter:

```text
DASHBOARD_REQUIRE_AUTH=true
DASHBOARD_ACCESS_USERNAME=your-private-username
DASHBOARD_ACCESS_PASSWORD=<your-private-unique-password>
THINGSPEAK_CHANNEL_ID=<channel-id>
THINGSPEAK_READ_KEY=<private-read-key>
```

The Blueprint sets `DASHBOARD_REQUIRE_AUTH=true` automatically and prompts for the username and password. Enter the actual values in Render's secure UI. **Never commit actual credentials to `render.yaml`, `.env.example`, README or GitHub**. Do not put your ThingSpeak Write key on Render.

After deployment, open the HTTPS site in a private/incognito browser window. Verify that it requests credentials. Try a wrong username, a wrong password, then the correct pair. After login, verify `/api/live` and `/api/export.csv` remain inaccessible without authentication.

Browser HTTP Basic credentials may remain cached during a browser session; closing all browser windows or using a fresh private window is the simplest way to test a logged-out state. Share credentials only with the intended professor or project team.

## Branch workflow

Merge this change into your local `main` development branch, run tests, push main, then promote the verified commit to `production` and push production. Render should then deploy the updated private site from the `production` branch.

## Account menu in the website

The top-right **User** button displays the actual `DASHBOARD_ACCESS_USERNAME` used for the authenticated Render session. Select the button to see the signed-in username and a protected-access indicator. The website gets this information from `/api/me`, which is protected by the same HTTP Basic Authentication as the dashboard; it does **not** expose the password or ThingSpeak secrets.

The local website has no authenticated identity unless login is explicitly enabled, so it displays **Local access** instead of inventing a username. The menu is informational; it does not change users, permissions, or Arduino behavior. A "Log out" button is intentionally not shown because browser HTTP Basic credential caching cannot be reliably cleared from a website button. Use a fresh private browser window to verify logged-out behavior.
