// Smart Electrocoagulator - INA219 logger for ESP32 (unit C1)
// Reads the INA219 every 1 s (paper: Tabel 3.9 T5, Gambar 3.3 "log CSV tiap 1 s")
// and prints one CSV line per reading over USB serial to the laptop.
// Wiring (Tabel 3.8): D1 GND INA219 -> GND ESP32; D3 VCC INA219 -> 3V3;
// D4 SDA INA219 -> GPIO 21; D5 SCL INA219 -> GPIO 22. D2 (GND ESP32 -> kaki 5) needs no code.

#include <Wire.h>
#include <Adafruit_INA219.h>

const int PIN_SDA = 21;                 // Tabel 3.8, kabel D4
const int PIN_SCL = 22;                 // Tabel 3.8, kabel D5
const unsigned long INTERVAL_MS = 1000; // paper: data INA219 tercatat tiap 1 detik
const unsigned long BAUD = 115200;      // ASSUMED: paper gives no baud rate; common ESP32 default
const uint8_t INA219_ADDR = 0x40;       // ASSUMED: module default (A0, A1 not bridged); paper gives no address

Adafruit_INA219 ina219(INA219_ADDR);
unsigned long nextTick;
bool lastOk = false;

void setup() {
  Serial.begin(BAUD);
  Wire.begin(PIN_SDA, PIN_SCL);
  // ASSUMED: library default calibration 32 V / 2 A (0.1 mA steps); covers the 24 V limit and 0.65 A max current.
  lastOk = ina219.begin(&Wire);
  if (!lastOk) Serial.println("# ERROR: INA219 not found at 0x40 - check D1, D3-D5");
  Serial.println("millis_ms,bus_V,current_mA,power_mW,status");
  nextTick = millis();
}

void loop() {
  if ((long)(millis() - nextTick) < 0) return;
  nextTick += INTERVAL_MS;  // fixed schedule, so the interval does not drift

  // A power glitch on the INA219 wipes its calibration register (current would read 0), so rewrite it after any failure.
  if (!lastOk) {
    ina219.setCalibration_32V_2A();
    delay(2);  // let one conversion (~0.5 ms) finish with the new calibration
  }

  unsigned long t = millis();
  float v = ina219.getBusVoltage_V();  // Vin- to GND = cell voltage (Gambar 3.3 note)
  bool ok = ina219.success();
  float mA = ina219.getCurrent_mA();
  ok = ok && ina219.success();
  float mW = ina219.getPower_mW();
  ok = ok && ina219.success();

  lastOk = ok;

  Serial.print(t);
  if (ok) {
    Serial.printf(",%.3f,%.1f,%.1f,OK\n", v, mA, mW);
  } else {
    Serial.println(",,,,ERR_I2C");  // line still printed so the laptop sees the ESP32 is alive (R20)
  }
}
