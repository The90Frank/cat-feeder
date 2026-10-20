# cat-feeder

Smart cat food dispenser built on **ESP32 + ESPHome + Home Assistant**.

- Dispenses a configurable portion through a 3D-printed auger driven by a NEMA 17 + TMC2209
- Identifies the cat by its collar tag (RFID 125 kHz or NFC 13.56 MHz)
- Feeds at most once per time slot; slots and portion size are configured in Home Assistant
- Reports the hopper fill level and raises a low-food alarm

The ESP32 is a plain sensor/actuator node; all business logic lives in Home Assistant.

## Layout

| Path | Content |
|---|---|
| `docs/` | Design plan and notes |
| `firmware/esphome/` | ESPHome device configuration |
| `homeassistant/` | Helpers, automations, scripts |
| `hardware/` | BOM, wiring diagrams |
| `cad/` | 3D-printable parts (STEP/STL) |

## Status

Design phase — see [`docs/plan.md`](docs/plan.md).
