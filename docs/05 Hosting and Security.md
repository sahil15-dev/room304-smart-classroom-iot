# Hosting and security

![Cloud deployment](../assets/deployment%20architecture.png)

## Deployment model

The laptop bridge holds the **ThingSpeak Write API key** and publishes measurements. Render hosts a Flask web service in cloud mode and uses a **private Read API key** to fetch recorded history. Render never accesses COM3 or operates the UNO directly.

The deployed web address is [Smart Classroom Sentinel](https://smart-classroom-sentinel.onrender.com/). It uses HTTP Basic Authentication where hosted credentials are configured. The browser can retain Basic Auth credentials after a tab closes; closing a tab is **not** a guaranteed logout.

## Render variables

| Key | Hosted value |
|:--|:--|
| `DASHBOARD_DATA_SOURCE` | `cloud` |
| `DASHBOARD_REQUIRE_AUTH` | `true` |
| `DASHBOARD_ACCESS_USERNAME` | Private username, entered in Render Environment |
| `DASHBOARD_ACCESS_PASSWORD` | Strong private password, entered in Render Environment |
| `THINGSPEAK_CHANNEL_ID` | Channel identifier matching the laptop bridge's upload channel |
| `THINGSPEAK_READ_KEY` | Private read-only API key |

The supplied `render.yaml` defines the hosted service and tracks changes from the configured GitHub deployment branch. The source code contains **no actual credentials**. The dashboard should fail closed when hosted authentication is required but credentials are missing.

## Operational behavior

- GitHub source availability and website access are separate: a public repository can host a password-protected dashboard.
- A private ThingSpeak channel protects the upstream feed; it does **not** automatically protect data displayed by the Flask site.
- The public `/api/health` endpoint is used for service health checks; sensor APIs require credentials in hosted mode.
- Render Free services can spin down after inactivity. The first visit can be slow; subsequent live readings are gated by ThingSpeak's upload cadence and fetch caching.
- A user who can log into the hosted site can read displayed history and export accessible cloud records.

## Key boundaries

Never commit local `.env`, real keys, passwords, logs containing private data or student identifiers. The repo's `.env.example` intentionally contains blank placeholder values. Keep `THINGSPEAK_WRITE_KEY` out of Render. A private dashboard read key should never appear in browser-side JavaScript.

The project is designed as an educational monitoring prototype, not as a hardened authentication platform. Basic Authentication has no application-level sign-out or expiring user session. HTTPS is essential for protecting credentials in transit.
