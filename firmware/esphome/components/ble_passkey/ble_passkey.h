#pragma once

#include <array>
#include <vector>

#include <esp_gap_ble_api.h>
#include <esp_gatts_api.h>

#include "esphome/core/component.h"

namespace esphome {
namespace ble_passkey {

class BLEPasskey : public Component {
 public:
  void loop() override;
  void dump_config() override;
  float get_setup_priority() const override { return setup_priority::AFTER_BLUETOOTH; }

  void set_passkey(uint32_t passkey) { this->passkey_ = passkey; }

  // True once the client on this connection paired (or reconnected bonded) with MITM.
  bool is_authenticated(uint16_t conn_id) const;
  // Removes every stored bond: phones must pair again.
  void clear_bonds();

  void gap_event_handler(esp_gap_ble_cb_event_t event, esp_ble_gap_cb_param_t *param);
  void gatts_event_handler(esp_gatts_cb_event_t event, esp_gatt_if_t gatts_if, esp_ble_gatts_cb_param_t *param);

 protected:
  struct Client {
    uint16_t conn_id;
    std::array<uint8_t, 6> bda;
    bool authenticated;
  };

  bool apply_security_();

  uint32_t passkey_{0};
  bool security_applied_{false};
  std::vector<Client> clients_;
};

}  // namespace ble_passkey
}  // namespace esphome
