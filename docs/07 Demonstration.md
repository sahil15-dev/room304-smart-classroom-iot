# Demonstration

## System walkthrough

The demonstration uses a powered Arduino UNO with connected sensors, a laptop running the Python bridge, an available ThingSpeak channel and the hosted website.

1. **Overview:** The dashboard displays recent environmental and activity inputs with freshness status and historical charts.
2. **Sensor response:** Changing light level modifies the raw brightness ADC. Moving in front of the PIR changes its digital motion output when the module's hold period permits. Magnet proximity can change the reed input.
3. **Comfort rule:** A deliberately configured test threshold produces a comfort-warning code, blue local LED and dashboard warning.
4. **Possible-lighting rule:** In expected-empty mode with bright illumination and no recorded activity for the quiet interval, a possible unnecessary-lighting warning appears with a red LED.
5. **Cloud trail:** New accepted serial readings are appended to a CSV, and successful ThingSpeak uploads become visible on the hosted overview and history pages.

The alert scenarios are demonstrations of the detection *logic*, not evidence that real energy waste occurred or that a room was definitely empty.

## Presenting real results

A complete engineering record distinguishes actual serial outputs and cloud uploads from illustrative examples and test-mode settings. If a sensor does not show the expected physical response, its limitation is disclosed rather than substituting simulated readings. The hosted browser UI is password protected, so demonstration credentials are supplied privately to authorized viewers only.

## Project outcome

The finished prototype connects low-cost sensing, embedded decisions, serial/cloud logging and a responsive web monitoring interface. It is intentionally conservative about occupancy inference and reports possible conditions for verification rather than automating building control.
