#pragma once

#include <string>
#include <vector>

#include "esphome/components/text_sensor/text_sensor.h"
#include "esphome/components/uart/uart.h"
#include "esphome/core/automation.h"
#include "esphome/core/component.h"

namespace esphome {
namespace fdx_b {

// WL-134 frame, 30 bytes:
//   [0]      0x02
//   [1..10]  national ID, 10 ASCII hex digits, least significant first
//   [11..14] country code, 4 ASCII hex digits, least significant first
//   [15]     data block flag
//   [16]     animal flag
//   [17..26] reserved
//   [27]     XOR of bytes 1..26
//   [28]     bitwise NOT of [27]
//   [29]     0x03
class FdxBReader : public Component, public uart::UARTDevice {
 public:
  static constexpr size_t FRAME_LEN = 30;

  void loop() override;
  void dump_config() override;
  float get_setup_priority() const override { return setup_priority::DATA; }

  void set_repeat_interval(uint32_t ms) { this->repeat_interval_ = ms; }
  void set_verify_checksum(bool verify) { this->verify_checksum_ = verify; }
  void set_last_tag_sensor(text_sensor::TextSensor *sensor) { this->last_tag_ = sensor; }
  void add_on_tag_callback(std::function<void(std::string)> &&callback) {
    this->callback_.add(std::move(callback));
  }

  // 15-digit ID as printed on pet passports: 3-digit country + 12-digit national ID.
  static std::string format_tag(uint16_t country, uint64_t national);
  // Builds a valid frame, for loopback self-tests.
  static std::vector<uint8_t> build_frame(uint16_t country, uint64_t national);

 protected:
  void process_frame_();
  static bool parse_reversed_hex_(const uint8_t *data, size_t len, uint64_t &out);

  uint8_t buffer_[FRAME_LEN];
  size_t pos_{0};
  std::string current_;
  uint32_t last_seen_{0};
  uint32_t repeat_interval_{5000};
  bool verify_checksum_{true};
  text_sensor::TextSensor *last_tag_{nullptr};
  CallbackManager<void(std::string)> callback_;
};

class TagTrigger : public Trigger<std::string> {
 public:
  explicit TagTrigger(FdxBReader *parent) {
    parent->add_on_tag_callback([this](std::string tag) { this->trigger(tag); });
  }
};

}  // namespace fdx_b
}  // namespace esphome
