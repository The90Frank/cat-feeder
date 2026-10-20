"""Minimal TMC2209 UART configuration: current, microsteps, StealthChop, StallGuard.

Motion stays on STEP/DIR (e.g. the a4988 stepper platform); this component only
programs the driver registers and re-applies them after a driver power cycle.
"""

import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import sensor, uart
from esphome.const import CONF_ADDRESS, CONF_ID, STATE_CLASS_MEASUREMENT

DEPENDENCIES = ["uart"]
AUTO_LOAD = ["sensor"]

CONF_RSENSE = "rsense"
CONF_RUN_CURRENT = "run_current"
CONF_HOLD_CURRENT = "hold_current"
CONF_MICROSTEPS = "microsteps"
CONF_STALL_THRESHOLD = "stall_threshold"
CONF_SG_RESULT = "sg_result"

MICROSTEPS = {256: 0, 128: 1, 64: 2, 32: 3, 16: 4, 8: 5, 4: 6, 2: 7, 1: 8}

tmc_ns = cg.esphome_ns.namespace("tmc2209_uart")
TMC2209 = tmc_ns.class_("TMC2209", cg.PollingComponent, uart.UARTDevice)

CONFIG_SCHEMA = (
    cv.Schema(
        {
            cv.GenerateID(): cv.declare_id(TMC2209),
            cv.Optional(CONF_ADDRESS, default=0): cv.int_range(0, 3),
            cv.Optional(CONF_RSENSE, default=0.11): cv.float_range(0.05, 1.0),
            cv.Optional(CONF_RUN_CURRENT, default=0.8): cv.float_range(0.05, 2.0),
            cv.Optional(CONF_HOLD_CURRENT, default=0.3): cv.float_range(0.0, 2.0),
            cv.Optional(CONF_MICROSTEPS, default=8): cv.one_of(*MICROSTEPS, int=True),
            cv.Optional(CONF_STALL_THRESHOLD, default=60): cv.int_range(0, 255),
            cv.Optional(CONF_SG_RESULT): sensor.sensor_schema(
                accuracy_decimals=0,
                state_class=STATE_CLASS_MEASUREMENT,
                icon="mdi:engine",
            ),
        }
    )
    .extend(cv.polling_component_schema("2s"))
    .extend(uart.UART_DEVICE_SCHEMA)
)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await uart.register_uart_device(var, config)
    cg.add(var.set_address(config[CONF_ADDRESS]))
    cg.add(var.set_rsense(config[CONF_RSENSE]))
    cg.add(var.set_currents(config[CONF_RUN_CURRENT], config[CONF_HOLD_CURRENT]))
    cg.add(var.set_mres(MICROSTEPS[config[CONF_MICROSTEPS]]))
    cg.add(var.set_stall_threshold(config[CONF_STALL_THRESHOLD]))
    if CONF_SG_RESULT in config:
        sens = await sensor.new_sensor(config[CONF_SG_RESULT])
        cg.add(var.set_sg_result_sensor(sens))
