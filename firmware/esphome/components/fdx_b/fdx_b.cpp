#include "fdx_b.h"

#include "esphome/core/helpers.h"
#include "esphome/core/log.h"

namespace esphome {
namespace fdx_b {

static const char *const TAG = "fdx_b";
static const uint8_t STX = 0x02;
static const uint8_t ETX = 0x03;

void FdxBReader::loop() {
  uint8_t byte;
  while (this->available() && this->read_byte(&byte)) {
    if (this->pos_ == 0 && byte != STX)
      continue;  // wait for the start of a frame
    this->buffer_[this->pos_++] = byte;
    if (this->pos_ < FRAME_LEN)
      continue;
    this->pos_ = 0;
    if (this->buffer_[FRAME_LEN - 1] == ETX) {
      this->process_frame_();
    } else {
      ESP_LOGW(TAG, "Frame without end marker, resyncing");
    }
  }
}

void FdxBReader::process_frame_() {
  uint8_t checksum = 0;
  for (size_t i = 1; i <= 26; i++)
    checksum ^= this->buffer_[i];
  if (checksum != this->buffer_[27] || static_cast<uint8_t>(~checksum) != this->buffer_[28]) {
    if (this->verify_checksum_) {
      ESP_LOGW(TAG, "Bad checksum: %s", format_hex_pretty(this->buffer_, FRAME_LEN).c_str());
      return;
    }
    ESP_LOGD(TAG, "Bad checksum ignored");
  }

  uint64_t national, country;
  if (!parse_reversed_hex_(this->buffer_ + 1, 10, national) ||
      !parse_reversed_hex_(this->buffer_ + 11, 4, country)) {
    ESP_LOGW(TAG, "Non-hex digits in frame: %s", format_hex_pretty(this->buffer_, FRAME_LEN).c_str());
    return;
  }

  std::string tag = format_tag(static_cast<uint16_t>(country), national);
  uint32_t now = millis();
  bool repeat = tag == this->current_ && now - this->last_seen_ < this->repeat_interval_;
  this->last_seen_ = now;
  if (repeat)
    return;  // still in the field

  this->current_ = tag;
  ESP_LOGI(TAG, "Tag %s (animal flag %c)", tag.c_str(), this->buffer_[16]);
  if (this->last_tag_ != nullptr)
    this->last_tag_->publish_state(tag);
  this->callback_.call(tag);
}

bool FdxBReader::parse_reversed_hex_(const uint8_t *data, size_t len, uint64_t &out) {
  out = 0;
  for (size_t i = len; i-- > 0;) {
    char c = static_cast<char>(data[i]);
    uint8_t v;
    if (c >= '0' && c <= '9') {
      v = c - '0';
    } else if (c >= 'A' && c <= 'F') {
      v = c - 'A' + 10;
    } else if (c >= 'a' && c <= 'f') {
      v = c - 'a' + 10;
    } else {
      return false;
    }
    out = (out << 4) | v;
  }
  return true;
}

std::string FdxBReader::format_tag(uint16_t country, uint64_t national) {
  return str_sprintf("%03u%012llu", country, static_cast<unsigned long long>(national));
}

std::vector<uint8_t> FdxBReader::build_frame(uint16_t country, uint64_t national) {
  static const char HEX[] = "0123456789ABCDEF";
  std::vector<uint8_t> frame(FRAME_LEN, '0');
  frame[0] = STX;
  for (size_t i = 0; i < 10; i++)
    frame[1 + i] = HEX[(national >> (4 * i)) & 0xF];
  for (size_t i = 0; i < 4; i++)
    frame[11 + i] = HEX[(country >> (4 * i)) & 0xF];
  frame[15] = '0';
  frame[16] = '1';
  uint8_t checksum = 0;
  for (size_t i = 1; i <= 26; i++)
    checksum ^= frame[i];
  frame[27] = checksum;
  frame[28] = static_cast<uint8_t>(~checksum);
  frame[29] = ETX;
  return frame;
}

void FdxBReader::dump_config() {
  ESP_LOGCONFIG(TAG, "FDX-B reader:");
  ESP_LOGCONFIG(TAG, "  Repeat interval: %u ms", this->repeat_interval_);
  ESP_LOGCONFIG(TAG, "  Verify checksum: %s", YESNO(this->verify_checksum_));
  LOG_TEXT_SENSOR("  ", "Last tag", this->last_tag_);
  this->check_uart_settings(9600);
}

}  // namespace fdx_b
}  // namespace esphome
