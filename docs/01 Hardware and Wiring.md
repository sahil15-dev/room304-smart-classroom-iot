# Hardware and wiring

![Room 304 complete wiring blueprint](../assets/wiring%20blueprint.png)

The editable circuit is available as [room 304 circuit.ckt](../assets/room%20304%20circuit.ckt) for opening in Cirkit Designer. The image and circuit reflect the assembled prototype; follow pin labels on the exact sensor modules and confirm continuity before applying power.

## Components

Arduino UNO R3, DHT11 (or a DHT22 only with the corresponding firmware setting), LDR/photoresistor module, analog Big Sound sensor, reed-switch module and magnet, PIR motion module, momentary button, RGB LED with individual resistors, active buzzer, breadboard and jumper wires. The USB cable connects the UNO to the laptop bridge.

| UNO | Device | Connection |
|:--|:--|:--|
| D2 | DHT11 | DATA |
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

## DHT11 wiring in the physical prototype

The prototype used a **bare four-pin DHT11 without an added external pull-up resistor**. The connection in the circuit drawing matches the assembled hardware:

- **VCC** → Arduino **5 V** supply rail
- **DATA** → Arduino **D2**
- **GND** → Arduino **GND** rail
- **NC** → left unconnected

This documents the as-built implementation, not a general rule for every DHT11 circuit. Bare DHT11 installations may require an external pull-up between VCC and DATA (often 4.7–10 kΩ) to ensure reliable readings, particularly with longer connections or a different board. No such resistor was added to this prototype.

## Configuration

The sketch is `firmware/Room304/Room304.ino`; hardware settings live in `firmware/Room304/config.h`. PIR sampling is active when `ENABLE_PIR=true`. The reed-switch input interpretation is controlled by `REED_CLOSED_IS_LOW`, and RGB polarity by `RGB_COMMON_ANODE`.

The actual LED requires one suitable resistor per color channel. The room wiring and sensor mounting are not the same as the illustrative dashboard seat schematic; the dashboard schematic is not a physical wiring guide.

## Practical placement

Keep the DHT11 away from direct heat, windows and the user's hand. Place the LDR where it can represent classroom illumination rather than direct flashlight glare. Mount reed and magnet so the intended open/closed positions produce distinct readings. PIR responds to changing infrared energy and needs time to settle after power-up. Microphone modules are not calibrated SPL meters; readings depend heavily on placement, wiring and module characteristics.
