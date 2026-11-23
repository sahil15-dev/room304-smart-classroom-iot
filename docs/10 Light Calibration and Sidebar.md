# Room 304 — Light calibration and sidebar update

This update changes only `dashboard/templates/index.html`. The existing Arduino firmware, Python serial bridge, `.env`, ThingSpeak API keys, and logged sensor data are not replaced.

## What changed

- **Continuous display-scale brightness:** The classroom floor-plan light cone and ambient-light meter now use a proportional brightness calculated from two sensor reference readings, rather than the full 0–1023 ADC scale. The cone smoothly fades during reading changes and can fully disappear at the measured dark reference.
- **Calibrate with your own environment:** Open **Test & calibrate → Light calibration**. With the sensor covered by a **nonconductive opaque cover**, click **Use current as dark**; with a flashlight on the sensor, click **Use current as bright**. Each button saves its captured value immediately. You can also enter values manually and click **Save calibration**. Values persist in that browser's local storage.
- **Data Pipeline stays at the bottom:** The desktop sidebar is fixed within the viewport, with the pipeline panel as its final block. The history table and test checklist still scroll independently. On mobile, the pipeline is hidden to preserve space.

## Important hardware safety

The small red light visible on a sensor board may be a **power LED**, not an indication of room brightness. The analog reading is the evidence: the observed module has **higher ADC values in the dark and lower ADC values in bright light**. A little ambient leakage is normal.

If you used aluminum foil, disconnect USB power first and remove it. Conductive foil could bridge exposed pins or PCB solder pads. Use opaque black paper or a nonconductive cap over the **light-sensitive component**, not the power connections.

## Why calibration helps

The approximate initial values are **dark ADC 790** and **bright ADC 110**, based on earlier project testing. These are editable starting points, **not universal sensor specifications**. The website computes relative brightness as:

`clamp(100 * (darkADC - currentADC) / (darkADC - brightADC), 0, 100)`

This is a relative display percentage, **not a lux measurement**. The result should vary continuously between 0% and 100% as light changes. It may still change abruptly if the actual sensor signal jumps, but the illustrated glow fades smoothly between updates.

**Firmware distinction:** This calibration only affects the website display. The Arduino lighting-waste warning still uses `LIGHT_BRIGHT_IS_HIGH` and `LIGHT_BRIGHT_THRESHOLD` in `firmware/Room304/config.h`. Test those separately before presenting the lighting-alert scenario. It does not control any classroom lights.

## Install without losing your working project

1. Stop only the website terminal (`Ctrl+C` in the terminal running `python -m dashboard.app`). The Arduino bridge can continue.
2. Extract the ZIP, then copy `dashboard/templates/index.html` into the **same path** of your original VS Code project. Allow replacing the old HTML file.
3. Add this guide under your project's `docs` folder.
4. Keep `.env`, the bridge, firmware, `platformio.ini`, ThingSpeak settings and Git data unchanged.
5. From the project root, run `python -m unittest discover -s tests -v`. Then restart the website with `python -m dashboard.app` and reload Chrome using `Ctrl+Shift+R`.
6. Open the **Test & calibrate** tab, set your actual dark and bright reference readings, and check the **Overview** meter and classroom light cone.
7. Scroll the Overview and Data History pages on desktop: Data Pipeline should stay anchored near the bottom-left of the viewport.

## GitHub

After verifying on the real laptop:

```powershell
git status
git add dashboard/templates/index.html "docs/10 Light Calibration and Sidebar.md"
git diff --cached --check
git ls-files .env
git commit -m "Calibrate dashboard light visualization and anchor sidebar pipeline"
git push
```

Do not commit `.env` or private ThingSpeak API keys. If Git says there is nothing to commit, check that you copied the file into the actual existing repository folder.
