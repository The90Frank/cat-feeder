# cat-feeder

Smart cat food dispenser built on **ESP32 + ESPHome**, with optional **Home Assistant** integration.

- Dispenses a configurable portion through a 3D-printed auger driven by a NEMA 17 + TMC2209
- Identifies the cat by its implanted microchip (FDX-B 134.2 kHz)
- Feeds at most once per time slot; slots and portion size are configurable remotely (Home Assistant) or locally (BLE)
- Measures the hopper level with a ToF laser, estimates remaining portions, detects auger jams (StallGuard)

The device is autonomous: feeding logic runs on the ESP32, configuration persists in flash, and time is kept by SNTP with a DS3231 RTC fallback. Home Assistant (Wi-Fi) and BLE are configuration channels, not requirements.

## Layout

| Path | Content |
|---|---|
| `docs/` | Design plan and notes |
| `firmware/esphome/` | ESPHome device configuration |
| `homeassistant/` | Dashboards and notification automations |
| `hardware/` | BOM, wiring diagrams |
| `cad/` | 3D-printable parts (STEP/STL) |

## Status

Design phase — see [`docs/plan.md`](docs/plan.md).
