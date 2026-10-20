#include "tmc2209_uart.h"

#include <cmath>

#include "esphome/core/hal.h"
#include "esphome/core/log.h"

namespace esphome {
namespace tmc2209_uart {

static const char *const TAG = "tmc2209_uart";

static const uint8_t SYNC = 0x05;
static const uint8_t REG_GCONF = 0x00;
static const uint8_t REG_GSTAT = 0x01;
static const uint8_t REG_IFCNT = 0x02;
static const uint8_t REG_IHOLD_IRUN = 0x10;
static const uint8_t REG_TCOOLTHRS = 0x14;
static const uint8_t REG_TPWMTHRS = 0x13;
static const uint8_t REG_SGTHRS = 0x40;
static const uint8_t REG_SG_RESULT = 0x41;
static const uint8_t REG_CHOPCONF = 0x6C;

// GCONF: pdn_disable (UART owns the PDN pin), mstep_reg_select (MRES from CHOPCONF),
// multistep_filt. en_SpreadCycle stays 0: StallGuard4 needs StealthChop.
static const uint32_t GCONF_VALUE = (1u << 6) | (1u << 7) | (1u << 8);
// CHOPCONF reset value (TOFF=3, HSTRT=5, intpol=1, vsense=0) with MRES cleared.
static const uint32_t CHOPCONF_BASE = 0x10000053u & ~(0xFu << 24);
static const float VFS = 0.325f;  // full-scale sense voltage, vsense = 0

void TMC2209::setup() {
  if (!this->apply_config_()) {
    ESP_LOGW(TAG, "No reply: driver unpowered or not wired. Will retry.");
    this->status_set_warning();
  }
}

void TMC2209::update() {
  uint32_t gstat;
  if (!this->read_register_(REG_GSTAT, gstat)) {
    if (this->configured_)
      ESP_LOGW(TAG, "Driver stopped answering");
    this->configured_ = false;
    this->status_set_warning();
    return;
  }
  // Reset flag, or first contact after a failed setup: (re)program the driver.
  if ((gstat & 0x01) || !this->configured_) {
    ESP_LOGI(TAG, "Driver %s: applying configuration", (gstat & 0x01) ? "reset" : "found");
    if (this->apply_config_())
      this->status_clear_warning();
    return;
  }
  if (this->sg_result_ != nullptr) {
    uint32_t sg;
    if (this->read_register_(REG_SG_RESULT, sg))
      this->sg_result_->publish_state(sg & 0x3FF);
  }
}

bool TMC2209::apply_config_() {
  uint32_t before, after;
  if (!this->read_register_(REG_IFCNT, before))
    return false;

  uint8_t irun = current_scale_(this->run_current_, this->rsense_);
  uint8_t ihold = current_scale_(this->hold_current_, this->rsense_);
  this->write_register_(REG_GCONF, GCONF_VALUE);
  this->write_register_(REG_CHOPCONF, CHOPCONF_BASE | (uint32_t(this->mres_) << 24));
  this->write_register_(REG_IHOLD_IRUN, ihold | (uint32_t(irun) << 8) | (6u << 16));
  this->write_register_(REG_TPWMTHRS, 0);         // StealthChop at every speed
  this->write_register_(REG_TCOOLTHRS, 0xFFFFF);  // StallGuard output at every speed
  this->write_register_(REG_SGTHRS, this->stall_threshold_);
  this->write_register_(REG_GSTAT, 0x07);         // clear reset/error flags

  // IFCNT counts accepted writes: 7 writes must have landed.
  if (!this->read_register_(REG_IFCNT, after) || ((after - before) & 0xFF) != 7) {
    ESP_LOGW(TAG, "Configuration not confirmed (IFCNT %u -> %u)", before & 0xFF, after & 0xFF);
    this->configured_ = false;
    return false;
  }
  ESP_LOGI(TAG, "Configured: IRUN %u, IHOLD %u, MRES %u, SGTHRS %u", irun, ihold, this->mres_,
           this->stall_threshold_);
  this->configured_ = true;
  return true;
}

void TMC2209::set_stall_threshold(uint8_t threshold) {
  this->stall_threshold_ = threshold;
  if (this->configured_ && !this->write_register_(REG_SGTHRS, threshold))
    ESP_LOGW(TAG, "SGTHRS write failed");
}

uint8_t TMC2209::current_scale_(float amps, float rsense) {
  // I_rms = (CS + 1) / 32 * VFS / (Rsense + 20 mOhm) / sqrt(2)
  float cs = amps * 32.0f * std::sqrt(2.0f) * (rsense + 0.02f) / VFS - 1.0f;
  if (cs < 0)
    return 0;
  if (cs > 31)
    return 31;
  return static_cast<uint8_t>(std::lround(cs));
}

uint8_t TMC2209::crc8_(const uint8_t *data, size_t len) {
  uint8_t crc = 0;
  for (size_t i = 0; i < len; i++) {
    uint8_t byte = data[i];
    for (int j = 0; j < 8; j++) {
      if ((crc >> 7) ^ (byte & 0x01)) {
        crc = (crc << 1) ^ 0x07;
      } else {
        crc = crc << 1;
      }
      byte >>= 1;
    }
  }
  return crc;
}

void TMC2209::drain_(size_t count, uint32_t timeout_ms) {
  uint32_t start = millis();
  uint8_t byte;
  while (count > 0 && millis() - start < timeout_ms) {
    if (this->available() && this->read_byte(&byte)) {
      count--;
    } else {
      yield();
    }
  }
}

bool TMC2209::write_register_(uint8_t reg, uint32_t value) {
  uint8_t frame[8] = {SYNC, this->address_, static_cast<uint8_t>(reg | 0x80),
                      static_cast<uint8_t>(value >> 24), static_cast<uint8_t>(value >> 16),
                      static_cast<uint8_t>(value >> 8), static_cast<uint8_t>(value), 0};
  frame[7] = crc8_(frame, 7);
  this->write_array(frame, sizeof(frame));
  this->flush();
  this->drain_(sizeof(frame), 10);  // echo
  return true;
}

bool TMC2209::read_register_(uint8_t reg, uint32_t &value) {
  uint8_t byte;
  while (this->available())
    this->read_byte(&byte);  // stale bytes

  uint8_t request[4] = {SYNC, this->address_, reg, 0};
  request[3] = crc8_(request, 3);
  this->write_array(request, sizeof(request));
  this->flush();
  this->drain_(sizeof(request), 10);  // echo

  uint8_t reply[8];
  size_t got = 0;
  uint32_t start = millis();
  while (got < sizeof(reply) && millis() - start < 20) {
    if (this->available() && this->read_byte(&reply[got])) {
      got++;
    } else {
      yield();
    }
  }
  if (got != sizeof(reply) || reply[0] != SYNC || reply[1] != 0xFF || reply[2] != reg ||
      reply[7] != crc8_(reply, 7))
    return false;
  value = (uint32_t(reply[3]) << 24) | (uint32_t(reply[4]) << 16) | (uint32_t(reply[5]) << 8) | reply[6];
  return true;
}

void TMC2209::dump_config() {
  ESP_LOGCONFIG(TAG, "TMC2209 (UART):");
  ESP_LOGCONFIG(TAG, "  Address: %u", this->address_);
  ESP_LOGCONFIG(TAG, "  Rsense: %.3f Ohm", this->rsense_);
  ESP_LOGCONFIG(TAG, "  Run / hold current: %.2f / %.2f A rms", this->run_current_, this->hold_current_);
  ESP_LOGCONFIG(TAG, "  MRES: %u", this->mres_);
  ESP_LOGCONFIG(TAG, "  Stall threshold: %u", this->stall_threshold_);
  ESP_LOGCONFIG(TAG, "  Configured: %s", YESNO(this->configured_));
  LOG_SENSOR("  ", "SG_RESULT", this->sg_result_);
  LOG_UPDATE_INTERVAL(this);
}

}  // namespace tmc2209_uart
}  // namespace esphome
