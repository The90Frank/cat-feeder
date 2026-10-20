#pragma once

#include "esphome/components/sensor/sensor.h"
#include "esphome/components/uart/uart.h"
#include "esphome/core/component.h"

namespace esphome {
namespace tmc2209_uart {

// Single-wire UART: TX through 1 kOhm to PDN_UART, RX direct. Every byte sent is
// echoed back on RX and is discarded before reading a reply.
class TMC2209 : public PollingComponent, public uart::UARTDevice {
 public:
  void setup() override;
  void update() override;
  void dump_config() override;
  float get_setup_priority() const override { return setup_priority::DATA; }

  void set_address(uint8_t address) { this->address_ = address; }
  void set_rsense(float rsense) { this->rsense_ = rsense; }
  void set_currents(float run, float hold) {
    this->run_current_ = run;
    this->hold_current_ = hold;
  }
  void set_mres(uint8_t mres) { this->mres_ = mres; }
  void set_sg_result_sensor(sensor::Sensor *sensor) { this->sg_result_ = sensor; }

  // StallGuard4: DIAG goes high when SG_RESULT <= 2 * threshold. Live-tunable.
  void set_stall_threshold(uint8_t threshold);
  bool is_configured() const { return this->configured_; }

 protected:
  bool apply_config_();
  bool write_register_(uint8_t reg, uint32_t value);
  bool read_register_(uint8_t reg, uint32_t &value);
  void drain_(size_t count, uint32_t timeout_ms);
  static uint8_t crc8_(const uint8_t *data, size_t len);
  static uint8_t current_scale_(float amps, float rsense);

  uint8_t address_{0};
  float rsense_{0.11f};
  float run_current_{0.8f};
  float hold_current_{0.3f};
  uint8_t mres_{5};
  uint8_t stall_threshold_{60};
  bool configured_{false};
  sensor::Sensor *sg_result_{nullptr};
};

}  // namespace tmc2209_uart
}  // namespace esphome
