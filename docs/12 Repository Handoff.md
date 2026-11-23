# Safe update to the existing GitHub repository

This repository preparation is **not a confirmed GitHub push or a Render deployment**. Merge the included files into your *existing* VS Code checkout. Do not create a second Git repository.

## Merge in Windows File Explorer

1. Save and close editors for files you intend to replace.
2. From the existing project root run `git status` to identify local edits; commit/back up anything you need before overwriting.
3. Extract the **repository update ZIP** and copy its folders/files into the *matching* locations of your existing `room304 smart classroom iot` directory.
4. Keep `.git`, `.env`, real `data/logs` files, and any other machine-specific secrets from your original checkout. **Do not replace or upload `.env`.**
5. The archive contains updated `README.md`, `assets` images and editable diagrams, synchronized `docs`, updated `dashboard/app.py` and frontend, refreshed `bridge/runner.py`, regression tests, `render.yaml`, `dashboard/requirements.txt`, `.env.example` and `.github/workflows/verify.yml`.

## Validate before committing

From the *same original VS Code project root*:

```powershell
python -m pip install -r requirements.txt -r dashboard/requirements.txt
python -m unittest discover -s tests -v
python -m compileall -q dashboard bridge tests

git status
git remote -v
# Confirm origin points to YOUR intended Room 304 repository.
git branch --show-current
```

If you have PlatformIO connected and want to re-check firmware, use **Project Tasks → uno → Build**. No Arduino pin map or firmware alert logic was changed in this repository documentation/deployment refresh.

## Stage safely

```powershell
git add README.md .env.example .gitignore render.yaml assets docs bridge/runner.py dashboard/app.py dashboard/templates/index.html dashboard/requirements.txt tests .github/workflows/verify.yml
git diff --cached --check
git diff --cached --stat
git diff --cached --name-only
git ls-files .env
```

**Expected:** `git ls-files .env` prints nothing. Inspect all staged file paths and contents. Never stage `.env`, API keys, screenshots containing tokens, or live student data. The project already ignores `data/logs` and `.env`.

Then commit and push to the branch you verified:

```powershell
git commit -m "Document Room 304 and prepare read-only online dashboard"
git push
```

If Git reports `nothing to commit`, check that the updated files were copied into the actual checkout. If push says upstream is missing, inspect `git branch -vv` and `git remote -v` rather than guessing a remote URL.

## After pushing

- Check GitHub README images render, especially **System Architecture**, **Pin Map**, and **Deployment Architecture**.
- Open **Actions → Verify project** and check for passing Python tests.
- Optionally create a Render Blueprint, set private Read key, and wait for its HTTPS URL; only then put the link in the GitHub About Website field.
- Tomorrow, add evidence and actual threshold measurements to `docs/04 Test Plan and Results.md`, then commit/push that validated update separately.

## What not to claim

- The Mini Reed, physical RGB LED/buzzer and PIR are **not yet verified**.
- The hosted URL does not exist until Render deploys it.
- A cloud dashboard showing old measurements does not mean the bridge is running.
- The prototype does not directly control electricity or prove classroom occupancy.
