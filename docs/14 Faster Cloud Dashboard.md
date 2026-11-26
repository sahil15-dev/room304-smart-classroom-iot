# Room 304 — Faster Cloud Dashboard (PIR + Login Preserved)

## What this updates

This is a targeted update for the existing Smart Classroom Sentinel **Render dashboard**. It does not change Arduino firmware, the microphone calibration, the Python serial bridge, ThingSpeak channel settings, or Render environment variables.

- Overview/Test fetch the **most recent 160** readings; Data History fetches the **full available 800** on demand. CSV export still uses the full 800 feed.
- Recent-cloud cache is **10 seconds** (previously 25 seconds). Full-history cache stays 25 seconds.
- Browser checks for new readings **every 5 seconds**, avoiding overlapping fetches.
- Main charts/cards redraw only on a new sensor reading, not on every poll.
- Cloud readings up to **90 seconds old** are accurately shown as **Recent cloud data**; older readings are marked delayed. This is *not* real-time socket streaming.
- The display now includes **PIR motion (D7)** and retains the private **user account menu**.

**Expected behavior:** Bridge uploads remain around every 20 seconds, so it is normal for the website to show a reading tens of seconds old. Render Free may also need time to wake after inactivity.

## Install safely (Windows, VS Code)

1. Open your actual project:
   `C:\Users\user\Desktop\git\room304\Room 304 Smart Classroom\room304 smart classroom iot`
2. In the project terminal run `git switch main` then `git status`. If there are **uncommitted changes**, preserve them before copying any files. Do not overwrite newer work.
3. **Back up** your current `dashboard/app.py` and `dashboard/templates/index.html` (Git works too).
4. Copy the files from this ZIP into the identical folders of your project:
   - `dashboard/app.py` → `dashboard/app.py`
   - `dashboard/templates/index.html` → `dashboard/templates/index.html`
   - `tests/testfastdashboard.py` → `tests/testfastdashboard.py`
   - `docs/14 Faster Cloud Dashboard.md` → `docs/14 Faster Cloud Dashboard.md`
5. Confirm Python dependencies are available (your existing dashboard setup should already have them).
6. Run `python -m unittest discover -s tests -v` and `git diff --check` from the project root. **If any test fails, stop: don't deploy until fixed.**
7. Check visually (optional local test): `python -m dashboard.app` then open `http://127.0.0.1:5000`. Stop it with Ctrl+C. Your bridge can continue feeding ThingSpeak separately.
8. Commit and push changes to development branch:
   ```powershell
   git add dashboard/app.py dashboard/templates/index.html tests/testfastdashboard.py "docs/14 Faster Cloud Dashboard.md"
   git commit -m "Improve cloud dashboard refresh and PIR display"
   git push origin main
   ```
9. Promote tested changes to your existing Render `production` branch:
   ```powershell
   git switch production
   git pull --ff-only origin production
   git merge --ff-only main
   git push origin production
   git switch main
   ```
   **If any git command fails, stop and inspect. Do not force-push.**
10. Render should redeploy from `production`. Wait for Live; open your protected URL in a fresh Incognito window to verify the login still works. Test `/api/live?recent=1` (small feed) and `/api/live` (full feed) while logged in. Check the PIR row, user menu, and History tab.

## Security and rollback

- Do not commit `.env`, password, ThingSpeak keys, or private screenshots.
- Keep `DASHBOARD_REQUIRE_AUTH=true` and your secret username/password in **Render Environment**. If login stops working, suspend the service until fixed.
- If the new version has a regression, restore the saved two files on `main`, run tests, and promote that restoration to `production`.
- The working serial bridge should stay running on your laptop for **new** cloud readings. Closing Render/GitHub browser tabs does not stop the deployment.

## Verification criteria

- `/api/live?recent=1` shows `source: cloud` with the correct current sensor values and has up to 160 entries.
- Overview's top-right age increases between uploads, then drops when a new cloud sample arrives; it should not refresh the entire chart every five seconds without data changes.
- Data History still provides up to 480 visible rows when selected and full available cloud CSV export.
- PIR reads digital 0/1 from D7 and no longer says `not installed`.
- User tab and login protection behave exactly as before.

**Note:** This patch was created against the latest dashboard and backend files previously prepared in this project. If you made new edits in VS Code since then, review the differences rather than blindly overwriting those edits.
