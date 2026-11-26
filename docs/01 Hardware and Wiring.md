# Hardware and wiring

![Arduino pin map](../assets/pin%20map.png)

## Components

Arduino UNO R3, DHT11 (or a DHT22 only with the corresponding firmware setting), LDR/photoresistor module, analog Big Sound sensor, reed-switch module and magnet, PIR motion module, momentary button, RGB LED with individual resistors, active buzzer, breadboard and jumper wires. The USB cable connects the UNO to the laptop bridge.

| UNO | Device | Connection |
|:--|:--|:--|
| D2 | DHT11 | Data |
| D3 | Reed switch | Digital input, internal pull-up |
| D4 | Button | Digital input, internal pull-up |
| D5 | Active buzzer | Digital output |
| D6 | RGB LED red | Resistor-limited output |
| D7 | PIR | Digital OUT, enabled by `ENABLE_PIR` |
| D9 | RGB LED green | Resistor-limited output |
| D10 | RGB LED blue | Resistor-limited output |
| A0 | LDR | Analog signal |
| A1 | Sound sensor | Analog **AO** (not digital DO) |
| 5V / GND | Compatible modules | Rated power and common ground |

Inspect the actual module silkscreen before wiring: pin orders vary. Disconnect USB power while changing connections. The PIR module's power input must be compatible with the supply voltage; this project assumes a module rated for Arduino 5 V operation. Never bridge the 5 V and GND rails. Do not power an inductive or high-current load directly from the UNO.

## Configuration

The sketch is `firmware/Room304/Room304.ino`; hardware settings live in `firmware/Room304/config.h`. The published pin allocation reserves D7 for PIR, while PIR sampling is active when `ENABLE_PIR=true`. The reed-switch input interpretation is controlled by `REED_CLOSED_IS_LOW`, and RGB polarity by `RGB_COMMON_ANODE`.

The actual LED requires one suitable resistor per channel. The room wiring and sensor mounting are not the same as the illustrative dashboard seat schematic; the illustration is not a physical wiring guide.

## Practical placement

Keep the DHT11 away from direct heat, windows and the user's hand. Place the LDR where it can represent classroom illumination rather than direct flashlight glare. Mount reed and magnet so the intended open/closed positions produce distinct readings. PIR responds to changing infrared energy and needs time to settle after power-up. Microphone modules are not calibrated SPL meters; readings depend heavily on placement, wiring and module characteristics.
