"""FDX-B (ISO 11784/11785, 134.2 kHz) reader over UART, e.g. the WL-134 module."""

import esphome.codegen as cg
import esphome.config_validation as cv
from esphome import automation
from esphome.components import text_sensor, uart
from esphome.const import CONF_ID, CONF_TRIGGER_ID

DEPENDENCIES = ["uart"]
AUTO_LOAD = ["text_sensor"]

CONF_ON_TAG = "on_tag"
CONF_LAST_TAG = "last_tag"
CONF_REPEAT_INTERVAL = "repeat_interval"
CONF_VERIFY_CHECKSUM = "verify_checksum"

fdx_b_ns = cg.esphome_ns.namespace("fdx_b")
FdxBReader = fdx_b_ns.class_("FdxBReader", cg.Component, uart.UARTDevice)
TagTrigger = fdx_b_ns.class_("TagTrigger", automation.Trigger.template(cg.std_string))

CONFIG_SCHEMA = (
    cv.Schema(
        {
            cv.GenerateID(): cv.declare_id(FdxBReader),
            # The same tag is reported again only after it has been absent this long.
            cv.Optional(CONF_REPEAT_INTERVAL, default="5s"): cv.positive_time_period_milliseconds,
            cv.Optional(CONF_VERIFY_CHECKSUM, default=True): cv.boolean,
            cv.Optional(CONF_LAST_TAG): text_sensor.text_sensor_schema(icon="mdi:chip"),
            cv.Optional(CONF_ON_TAG): automation.validate_automation(
                {cv.GenerateID(CONF_TRIGGER_ID): cv.declare_id(TagTrigger)}
            ),
        }
    )
    .extend(cv.COMPONENT_SCHEMA)
    .extend(uart.UART_DEVICE_SCHEMA)
)

FINAL_VALIDATE_SCHEMA = uart.final_validate_device_schema(
    "fdx_b", baud_rate=9600, require_rx=True
)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await uart.register_uart_device(var, config)
    cg.add(var.set_repeat_interval(config[CONF_REPEAT_INTERVAL]))
    cg.add(var.set_verify_checksum(config[CONF_VERIFY_CHECKSUM]))
    if CONF_LAST_TAG in config:
        sens = await text_sensor.new_text_sensor(config[CONF_LAST_TAG])
        cg.add(var.set_last_tag_sensor(sens))
    for conf in config.get(CONF_ON_TAG, []):
        trigger = cg.new_Pvariable(conf[CONF_TRIGGER_ID], var)
        await automation.build_automation(trigger, [(cg.std_string, "x")], conf)
