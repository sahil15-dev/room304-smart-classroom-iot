# Online dashboard — Render + GitHub auto-deploy

![Architecture](../assets/deployment%20architecture.png)

## The important distinction

There are two processes, **not one**:

- The **laptop bridge** (`python -m bridge.runner`) owns Arduino's COM port, writes a local CSV and uploads to ThingSpeak with the **Write API Key**.
- The **online website** (Render) runs only Flask, reads ThingSpeak with the private **Read API Key**, and offers a read-only web UI. Render does **not** connect to USB, control the Arduino, record audio, or write to ThingSpeak.

When the laptop bridge is off, ThingSpeak retains earlier records and the online site stays accessible (subject to the hosting plan), but new readings stop arriving. The website must show delayed/stale data instead of pretending the sensors are live.

## Recommended hosting: Render Blueprint

A `render.yaml` file is at repository root. It defines a Python web service with the GitHub auto-deploy trigger enabled and a health check endpoint.

1. In your existing VS Code checkout, review and commit the files in [Repository Handoff](12%20Repository%20Handoff.md), then push the correct branch to GitHub.
2. Visit https://dashboard.render.com/ and log in. Choose **New → Blueprint** (the exact menu can vary) and connect the **specific private Room 304 GitHub repository**. If Render cannot see it, update its GitHub repository permissions to allow access to *only this repo*.
3. Select the branch holding `render.yaml`. Render reads its build/start commands. Choose the free plan for a demo, or a paid plan if you require no idle sleeping.
4. Enter the prompted **`THINGSPEAK_CHANNEL_ID`** and **`THINGSPEAK_READ_KEY`** in Render. Never enter `THINGSPEAK_WRITE_KEY` on the hosted site. The Blueprint sets `DASHBOARD_DATA_SOURCE=cloud`.
5. Optionally set **`DASHBOARD_ACCESS_PASSWORD`** in Render → service → Environment to restrict sensor history with a browser password prompt. Do not place this password in GitHub.
6. Deploy and wait for Render's status to show the service is running. Visit the service's **actual** assigned `https://...onrender.com` URL. It should load the same three-page website.
7. Confirm `/api/health` returns `ok:true`, `/api/live` reports `source:"cloud"`, and cloud data matches ThingSpeak. Confirm it becomes stale after you stop the laptop bridge and wait long enough.
8. In GitHub, open your **existing Room 304 repository → About → gear icon → Website** and paste the Render URL. Add it to the top of README after it exists.

**Don't put placeholder site URLs in GitHub About.** The URL is created by Render after deployment.

## Auto-update workflow

Once the Render service is linked to your GitHub branch:

```powershell
# Edit website locally in VS Code; verify locally.
python -m unittest discover -s tests -v

git status
git add dashboard README.md docs assets render.yaml .github/workflows/verify.yml
git diff --cached --check
git diff --cached --name-only
# Review before committing; ensure no .env, secrets or private logs.
git commit -m "Update Smart Classroom Sentinel website"
git push
```

Every push to the selected branch triggers Render's deployment automatically. **Saving a file on your laptop alone does not update the online website**; you must commit/push, and Render must finish the deployment. The included GitHub Actions workflow also checks Python tests on pushes and PRs. It does not remotely deploy or control the Arduino.

## Running locally versus remotely

| Feature | Local website | Hosted website |
| -- | -- | -- |
| `DASHBOARD_DATA_SOURCE` | `local` | `cloud` |
| Source of readings | Laptop CSV | ThingSpeak REST API |
| Full local CSV export | Yes | No; exports fetched cloud records |
| Internet required for newest local readings | No | Yes |
| USB serial connection | Bridge uses it | None |
| API key exposed in browser | Never | Never; server-side only |
| Site usable after laptop is off | No | Yes, with last uploaded cloud records |
| Automatically updates code on GitHub push | Not needed | Yes, with Render Git integration |

## Privacy and reliability

A ThingSpeak *private* channel protects direct API access. **Anyone allowed to open your hosted dashboard can still read the sensor readings that the dashboard displays.** Protect it with `DASHBOARD_ACCESS_PASSWORD` or obtain appropriate permission before making the data public. Use only a read-only key on Render. Do not expose ThingSpeak write keys, raw classroom photos without consent, personal details, or secrets.

The free Render tier may **spin down after 15 minutes without traffic**; the next visitor may have to wait for it to wake. A paid plan can avoid idle sleeping. Render's local filesystem is ephemeral; the cloud-mode dashboard deliberately uses ThingSpeak history instead of a cloud CSV file.

The hosted dashboard polls `/api/live` frequently, but the server caches ThingSpeak API responses for ~25 seconds to avoid unnecessary requests. Cloud-mode Data History shows up to 800 recently fetched records (not the entire history of the channel). Local mode still exports the complete CSV file.

**Render references:** [Deploy Flask](https://render.com/docs/deploy-flask), [Blueprint specification](https://render.com/docs/blueprint-spec), [free plan limitations](https://render.com/docs/free). [ThingSpeak read API](https://www.mathworks.com/help/thingspeak/readdata.html).
