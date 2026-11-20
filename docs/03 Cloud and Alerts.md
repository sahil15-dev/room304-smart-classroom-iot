# ThingSpeak and Telegram setup

## ThingSpeak channel

1. Sign into https://thingspeak.mathworks.com/ and choose Channels -> My Channels -> New Channel.
2. Channel name: `Room 304 Smart Classroom` (private during development).
3. Enable field names in this **exact order**:

| Field | Name | Range/meaning |
| --- | --- | --- |
| 1 | Temperature (C) | DHT °C or omitted on failure |
| 2 | Humidity (%) | DHT relative humidity or omitted on failure |
| 3 | Light Level | Raw analog 0–1023, not calibrated lux |
| 4 | Sound Activity | Relative peak span, not dB |
| 5 | Door Open | 0/1 |
| 6 | Expected Empty | 0/1 selected by button |
| 7 | Alert Code | 0 normal, 1 comfort, 2 possible lighting, 3 sensor fault |
| 8 | PIR Motion | 0 until PIR is installed next week |

4. Save the channel, find the **Write API Key** on API Keys tab, and store it ONLY in local `.env`.
5. Keep uploads >=15 seconds apart for a free ThingSpeak channel. The bridge uses 20 seconds by default.
6. Start the Python bridge and confirm a new entry every ~20 sec while the laptop is connected.

## Telegram notifications

1. On Telegram, find the official verified `@BotFather`; create a new bot with `/newbot`.
2. Open your new bot and send `/start` or a test message.
3. Retrieve the chat ID through Telegram's `getUpdates` Bot API response in a **private environment**. Do not share API token or full token-bearing URL in screenshots, issues or chat logs.
4. Add `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` to local `.env`.
5. Start the bridge. It sends a warning when alert code changes and limits repetition for the same alarm to 5 min.
6. To test: temporarily adjust comfort or lighting thresholds in `config.h`, trigger a warning, confirm message, then restore the normal thresholds.

## Power and behavior

- The laptop must remain connected/running for Python-based ThingSpeak and Telegram integration. The UNO's local alarm continues without internet.
- The Python bridge must have exclusive access to the COM port. Close Arduino IDE/PlatformIO serial monitor while it runs.
- Never commit `.env`, token, key, private CSV logs or screenshots containing credentials.
- Keep the ThingSpeak channel private until you have checked all published fields.
- HTTP failures can occur because of authentication, limits, or networking. Check actual cloud dashboard, not just serial terminal output.

## Quick troubleshooting

| Symptom | Check |
|---|---|
| `could not open port COM3` | Actual COM port; close other serial monitors; USB driver/data cable |
| `No module named serial` | `python -m pip install -r requirements.txt` |
| Data logs but cloud does not update | Write API key, network, correct channel, 20-second interval |
| ThingSpeak write rejected | Invalid/revoked key, API response, write rate |
| No Telegram messages | Token, chat ID, bot conversation started, current alert nonzero |
| Telegram repeats too often | Confirm alert cooldown and whether alert state changes repeatedly |
| Unexpected cloud fields | Check exact field mapping above and parser unit tests |

References: https://www.mathworks.com/help/thingspeak/writedata.html and https://core.telegram.org/bots/api
