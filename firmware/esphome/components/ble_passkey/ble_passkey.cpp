#include "ble_passkey.h"

#include <cstring>

#include "esphome/components/esp32_ble/ble.h"
#include "esphome/core/log.h"

namespace esphome {
namespace ble_passkey {

static const char *const TAG = "ble_passkey";

void BLEPasskey::loop() {
  // Security parameters need an initialised Bluedroid stack.
  if (esp32_ble::global_ble == nullptr || !esp32_ble::global_ble->is_active())
    return;
  if (this->apply_security_()) {
    this->security_applied_ = true;
    this->disable_loop();
  }
}

bool BLEPasskey::apply_security_() {
  uint32_t passkey = this->passkey_;
  esp_ble_auth_req_t auth = ESP_LE_AUTH_REQ_SC_MITM_BOND;
  esp_ble_io_cap_t iocap = ESP_IO_CAP_OUT;  // we "display" the passkey: it is on the sticker
  uint8_t key_size = 16;
  uint8_t keys = ESP_BLE_ENC_KEY_MASK | ESP_BLE_ID_KEY_MASK;
  uint8_t only_specified = ESP_BLE_ONLY_ACCEPT_SPECIFIED_AUTH_ENABLE;

  bool ok = esp_ble_gap_set_security_param(ESP_BLE_SM_SET_STATIC_PASSKEY, &passkey, sizeof(passkey)) == ESP_OK;
  ok &= esp_ble_gap_set_security_param(ESP_BLE_SM_AUTHEN_REQ_MODE, &auth, sizeof(auth)) == ESP_OK;
  ok &= esp_ble_gap_set_security_param(ESP_BLE_SM_IOCAP_MODE, &iocap, sizeof(iocap)) == ESP_OK;
  ok &= esp_ble_gap_set_security_param(ESP_BLE_SM_MAX_KEY_SIZE, &key_size, sizeof(key_size)) == ESP_OK;
  ok &= esp_ble_gap_set_security_param(ESP_BLE_SM_SET_INIT_KEY, &keys, sizeof(keys)) == ESP_OK;
  ok &= esp_ble_gap_set_security_param(ESP_BLE_SM_SET_RSP_KEY, &keys, sizeof(keys)) == ESP_OK;
  ok &= esp_ble_gap_set_security_param(ESP_BLE_SM_ONLY_ACCEPT_SPECIFIED_SEC_AUTH, &only_specified,
                                       sizeof(only_specified)) == ESP_OK;
  if (!ok) {
    ESP_LOGE(TAG, "Failed to set security parameters");
    this->mark_failed();
    return false;
  }
  ESP_LOGI(TAG, "Static passkey pairing enabled (SC + MITM + bonding)");
  return true;
}

bool BLEPasskey::is_authenticated(uint16_t conn_id) const {
  for (const auto &c : this->clients_) {
    if (c.conn_id == conn_id)
      return c.authenticated;
  }
  return false;
}

void BLEPasskey::clear_bonds() {
  int count = esp_ble_get_bond_device_num();
  if (count <= 0)
    return;
  std::vector<esp_ble_bond_dev_t> list(count);
  esp_ble_get_bond_device_list(&count, list.data());
  for (int i = 0; i < count; i++)
    esp_ble_remove_bond_device(list[i].bd_addr);
  ESP_LOGI(TAG, "Removed %d bonded device(s)", count);
}

void BLEPasskey::gatts_event_handler(esp_gatts_cb_event_t event, esp_gatt_if_t gatts_if,
                                     esp_ble_gatts_cb_param_t *param) {
  switch (event) {
    case ESP_GATTS_CONNECT_EVT: {
      Client c{param->connect.conn_id, {}, false};
      std::memcpy(c.bda.data(), param->connect.remote_bda, 6);
      this->clients_.push_back(c);
      // Ask for an authenticated link right away: the phone shows the passkey prompt.
      esp_ble_set_encryption(param->connect.remote_bda, ESP_BLE_SEC_ENCRYPT_MITM);
      ESP_LOGD(TAG, "Client %u connected, requesting pairing", param->connect.conn_id);
      break;
    }
    case ESP_GATTS_DISCONNECT_EVT: {
      uint16_t conn_id = param->disconnect.conn_id;
      for (auto it = this->clients_.begin(); it != this->clients_.end(); ++it) {
        if (it->conn_id == conn_id) {
          this->clients_.erase(it);
          break;
        }
      }
      break;
    }
    default:
      break;
  }
}

void BLEPasskey::gap_event_handler(esp_gap_ble_cb_event_t event, esp_ble_gap_cb_param_t *param) {
  switch (event) {
    case ESP_GAP_BLE_SEC_REQ_EVT:
      esp_ble_gap_security_rsp(param->ble_security.ble_req.bd_addr, true);
      break;
    case ESP_GAP_BLE_PASSKEY_NOTIF_EVT:
      ESP_LOGI(TAG, "Pairing: enter the passkey from the sticker on the phone");
      break;
    case ESP_GAP_BLE_AUTH_CMPL_EVT: {
      const auto &auth = param->ble_security.auth_cmpl;
      bool mitm = (auth.auth_mode & ESP_LE_AUTH_REQ_MITM) != 0;
      bool ok = auth.success && mitm;
      for (auto &c : this->clients_) {
        if (std::memcmp(c.bda.data(), auth.bd_addr, 6) == 0)
          c.authenticated = ok;
      }
      if (ok) {
        ESP_LOGI(TAG, "Client authenticated");
      } else {
        ESP_LOGW(TAG, "Pairing failed (reason 0x%02X, MITM %s)", auth.fail_reason, YESNO(mitm));
      }
      break;
    }
    default:
      break;
  }
}

void BLEPasskey::dump_config() {
  ESP_LOGCONFIG(TAG, "BLE passkey pairing:");
  ESP_LOGCONFIG(TAG, "  Security applied: %s", YESNO(this->security_applied_));
  ESP_LOGCONFIG(TAG, "  Bonded devices: %d", esp_ble_get_bond_device_num());
}

}  // namespace ble_passkey
}  // namespace esphome
