# Home Assistant

The feeder works without Home Assistant. When it is connected (ESPHome integration), every entity appears automatically; this folder only adds notifications.

## Notifications blueprint

[`blueprints/automation/cat_feeder_notifications.yaml`](blueprints/automation/cat_feeder_notifications.yaml) sends push notifications to the companion app.

| Notification | Source |
|---|---|
| The cat has eaten | `fed` event |
| Manual feed (Home Assistant / BLE) | `manual_feed_ha`, `manual_feed_ble` events |
| Missed meal | `slot_missed_1..3` events, raised by the device at the end of each slot |
| Hopper empty when the cat came | `hopper_empty` event |
| Auger jammed | `auger_jammed` event |
| Clock not valid | `time_invalid` event |
| Food running low | "Doses left" sensor below a threshold |
| Device offline | "Doses left" unavailable for N minutes |

Every notification can be turned off, and every message can be translated.

### Import

[![Open your Home Assistant instance and show the blueprint import dialog with a specific blueprint pre-filled.](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FThe90Frank%2Fcat-feeder%2Fblob%2Fmain%2Fhomeassistant%2Fblueprints%2Fautomation%2Fcat_feeder_notifications.yaml)

Or: *Settings → Automations & scenes → Blueprints → Import blueprint*, with the URL:

```text
https://github.com/The90Frank/cat-feeder/blob/main/homeassistant/blueprints/automation/cat_feeder_notifications.yaml
```

### Configure

*Create automation* from the blueprint, then pick:

1. **Feeder event entity**: `event.…_feeder_event`
2. **Doses left sensor**: `sensor.…_doses_left`
3. **Phone**: a device with the companion app
4. Notifications to send, low food threshold, offline delay
5. **Messages** (collapsed section): translate the texts. `{slot}` and `{doses}` are replaced with the slot number and the doses left

### Notes

- "Doses left" stays unknown until the device has learned the level drop per dose: the low food alert starts after the first feeds
- "Missed meal" is skipped while the feeder is paused, and only for cats with an authorized chip
