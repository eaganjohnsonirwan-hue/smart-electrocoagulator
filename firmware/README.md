# Firmware for unit C1 (Smart Electrocoagulator)

Two programs, both Arduino C++:

| Folder | Board | What it does |
|---|---|---|
| `logger/` | ESP32 (DevKit, "ESP32 Dev Module") | Reads the INA219 every 1 s and prints CSV to the laptop over USB |
| `camera/` | ESP32-CAM AI-Thinker | Web server: `/capture` returns one JPEG with locked exposure, gain and white balance |

Compiled 2026-11-25 with arduino-cli 1.6.0, ESP32 core 3.3.13; not yet tested on hardware.
Compile output: `2026-11-25_compile-log_v01.txt`.

## Board settings

| Program | FQBN (arduino-cli) | Arduino IDE menu |
|---|---|---|
| logger | `esp32:esp32:esp32` | Tools > Board > esp32 > ESP32 Dev Module, defaults |
| camera | `esp32:esp32:esp32cam` | Tools > Board > esp32 > AI Thinker ESP32-CAM, defaults (PSRAM on) |

Board package URL: `https://espressif.github.io/arduino-esp32/package_esp32_index.json`

## Libraries

| Library | Version | Used by |
|---|---|---|
| Adafruit INA219 | 1.2.3 | logger |
| Adafruit BusIO (installed with INA219) | 1.17.4 | logger |
| esp32-camera, WiFi, WebServer, Wire | bundled with ESP32 core 3.3.13 | camera, logger |

## Pin table (checked against Tabel 3.8 and Gambar 3.3 / 3.6)

| Cable (Tabel 3.8) | From | To | In code |
|---|---|---|---|
| D1 | GND INA219 | GND ESP32 | no code (ground) |
| D2 | second GND pin ESP32 | switch leg 5 | no code (ground) |
| D3 | VCC INA219 | 3V3 ESP32 | no code (power) |
| D4 | SDA INA219 | GPIO 21 ESP32 | `PIN_SDA = 21` in `logger.ino` |
| D5 | SCL INA219 | GPIO 22 ESP32 | `PIN_SCL = 22` in `logger.ino` |
| K1 | USB charger 5 V | 5V and GND ESP32-CAM | no code (power) |
| (text, Langkah 3) | flash LED | GPIO 4 ESP32-CAM | `PIN_FLASH_LED = 4`, held LOW (off) |
| USB cable | ESP32 micro-USB | laptop | `Serial`, 115200 baud |

The camera's own pins (OV2640 data, clock, SCCB) are fixed on the AI-Thinker board; the code uses the standard AI-Thinker map.

## How to upload

1. Logger: plug the ESP32 into the laptop with the USB data cable.
   `arduino-cli upload -p COMx --fqbn esp32:esp32:esp32 logger`
   (Arduino IDE: open `logger/logger.ino`, pick the board and port, Upload.)
2. Camera: copy `camera/secrets.h.example` to `camera/secrets.h` and fill in the Wi-Fi name and password (never commit `secrets.h`; it is in `.gitignore`).
   Put the ESP32-CAM on its programming board, plug it in, then
   `arduino-cli compile --fqbn esp32:esp32:esp32cam camera` and `arduino-cli upload -p COMx --fqbn esp32:esp32:esp32cam camera`.
   Open the serial monitor at 115200 once to read the IP address, then remove the programming board (paper, Langkah 3).
3. arduino-cli on this PC: `%LOCALAPPDATA%\arduino-cli\arduino-cli.exe`. Board data lives in `C:\a15` (short path: inside the Claude app the default Arduino15 path is redirected to a longer one and the compiler hit the 260-character Windows path limit). The ESP32 core is pinned at 3.3.13 because 4.0.0 is a 2.3 GB download.

## Logger CSV format

Serial 115200 baud. First line is the header, then one line per second:

```
millis_ms,bus_V,current_mA,power_mW,status
12000,3.712,650.3,2413.9,OK
13000,,,,ERR_I2C
```

- `millis_ms`: ms since the ESP32 started (laptop adds the clock time when saving).
- `bus_V`: INA219 bus voltage = Vin- to GND = cell voltage U (Gambar 3.3 note).
- `current_mA`, `power_mW`: from the INA219 (32 V / 2 A calibration, 0.1 mA steps).
- `status`: `OK`, or `ERR_I2C` when any INA219 read fails; the value fields are then empty. The line is still sent each second so the laptop can tell an INA219 fault from a lost USB link (R20: no line for > 10 s = logging stopped).
- Lines starting with `#` are messages (for example INA219 not found at start-up); skip them when parsing.
- After a failed read, the next tick rewrites the INA219 calibration first (a power glitch on the module clears it and current would read 0).

## Camera use

`http://<ip>/capture?batch=<batch code>&n=<1..3>` returns one fresh JPEG with file name `<batch>_<n>.jpg`.
The paper takes three photos per sample, so the laptop calls it three times, for example:
`curl -o T5-B07-akhir_1.jpg "http://<ip>/capture?batch=T5-B07-akhir&n=1"`.
The first frame in the buffer is dropped so each photo is taken after the request (door closed, LED on).
Only letters, digits, `-` and `_` are kept in the batch code.

## Choices not in the paper

| Item | Choice | Why |
|---|---|---|
| Serial baud rate | 115200 | Common ESP32 default; paper gives none |
| INA219 I2C address | 0x40 | Module default with A0/A1 not bridged |
| INA219 calibration | 32 V / 2 A (library default) | Covers the 24 V limit and 0.65 A maximum |
| CSV columns and `status` flag | as above | Brief asked for millis, V, mA, mW plus a read-failure flag |
| Camera pin map | standard AI-Thinker | Paper names the AI-Thinker board but no camera pins |
| Resolution | SVGA 800 x 600 | Analysis only needs a fixed 100 x 100 px area |
| JPEG quality | 10 | Low compression keeps colour averages stable |
| Exposure value | 300 (0-1200), auto exposure off | Placeholder, set once at T1 |
| Gain | 0 (1x), auto gain off | Least noise; set once at T1 |
| White balance | preset 3 (office), auto white balance off | Placeholder, set once at T1 |
| Wi-Fi mode | station (joins an existing network) | Paper says only "via Wi-Fi ke laptop" |
| Photo transfer | laptop pulls over HTTP port 80 (`/capture`) | Simplest; paper does not say push or pull |
| Photo timing | on command only | T3 minute 10/20/30 are sampling times; each sample is photographed after it is placed in the optical chamber |
| Camera serial 115200 | debug only (shows IP) | Needs the programming board attached |

The exposure, gain and white-balance values are compile-time constants at the top of `camera.ino`. Tune them at T1, then do not change them for the rest of the tests (paper: settings locked since T1).
