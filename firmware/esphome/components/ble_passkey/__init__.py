"""Static-passkey BLE pairing for a GATT server, plus per-connection auth tracking.

ESPHome sets the pairing mode but neither a static passkey nor encrypted
characteristic permissions. This component asks every new client to pair with
MITM protection and tells on_write handlers whether the connection is trusted.
"""

import re

import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import esp32_ble
from esphome.const import CONF_ID

DEPENDENCIES = ["esp32_ble"]

CONF_PASSKEY = "passkey"

ble_passkey_ns = cg.esphome_ns.namespace("ble_passkey")
BLEPasskey = ble_passkey_ns.class_("BLEPasskey", cg.Component)


def validate_passkey(value):
    value = cv.string_strict(value)
    if not re.fullmatch(r"\d{6}", value):
        raise cv.Invalid("passkey must be exactly 6 digits")
    if value == "000000":
        raise cv.Invalid("replace the placeholder passkey 000000 in secrets.yaml")
    return int(value)


CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(): cv.declare_id(BLEPasskey),
        cv.GenerateID(esp32_ble.CONF_BLE_ID): cv.use_id(esp32_ble.ESP32BLE),
        cv.Required(CONF_PASSKEY): validate_passkey,
    }
).extend(cv.COMPONENT_SCHEMA)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    parent = await cg.get_variable(config[esp32_ble.CONF_BLE_ID])
    esp32_ble.register_gap_event_handler(parent, var)
    esp32_ble.register_gatts_event_handler(parent, var)
    cg.add(var.set_passkey(config[CONF_PASSKEY]))
