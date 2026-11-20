"""Room 304 serial protocol validation; no external dependencies."""
from dataclasses import dataclass
import csv
import math


@dataclass(frozen=True)
class Reading:
    temperature_c: float | None
    humidity_percent: float | None
    light: int
    sound_span: int
    door_open: int
    expected_empty: int
    alert_code: int
    pir_motion: int


def _optional_finite_float(value: str) -> float | None:
    result = float(value)
    return result if math.isfinite(result) else None


def parse_serial_line(line: str) -> Reading | None:
    """Return None for INFO/invalid readings. Expect 8 data fields after DATA."""
    if not line.startswith('DATA,'):
        return None
    try:
        fields = next(csv.reader([line.strip()]))
        if len(fields) != 9 or fields[0] != 'DATA':
            return None
        temperature = _optional_finite_float(fields[1])
        humidity = _optional_finite_float(fields[2])
        light, sound, door, expected, alert, pir = map(int, fields[3:])
        if not (0 <= light <= 1023 and 0 <= sound <= 1023):
            return None
        if any(v not in (0, 1) for v in (door, expected, pir)):
            return None
        if alert not in (0, 1, 2, 3):
            return None
        # Missing temp/humidity is allowed only for alert code 3.
        if alert != 3 and (temperature is None or humidity is None):
            return None
        return Reading(temperature, humidity, light, sound, door, expected, alert, pir)
    except (ValueError, TypeError, StopIteration, OverflowError):
        return None


def thingspeak_fields(reading: Reading) -> dict[str, int | float]:
    """Return up to eight ThingSpeak fields; no API key stored here."""
    fields: dict[str, int | float] = {
        'field3': reading.light,
        'field4': reading.sound_span,
        'field5': reading.door_open,
        'field6': reading.expected_empty,
        'field7': reading.alert_code,
        'field8': reading.pir_motion,
    }
    if reading.temperature_c is not None:
        fields['field1'] = reading.temperature_c
    if reading.humidity_percent is not None:
        fields['field2'] = reading.humidity_percent
    return fields


def alert_message(reading: Reading) -> str | None:
    messages = {1: 'Temperature/humidity outside calibrated comfort range',
                2: 'Possible unnecessary classroom lighting; please verify',
                3: 'Temperature/humidity sensor reading failed'}
    if reading.alert_code == 0:
        return None
    return (f'ROOM 304 ALERT\n{messages[reading.alert_code]}\n'
            f'Temp: {reading.temperature_c} C, humidity: {reading.humidity_percent}%\n'
            f'Light: {reading.light}, sound activity: {reading.sound_span}\n'
            f'Expected empty: {"YES" if reading.expected_empty else "NO"}')
