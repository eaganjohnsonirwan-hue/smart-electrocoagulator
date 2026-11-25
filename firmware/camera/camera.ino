// Smart Electrocoagulator - ESP32-CAM (AI-Thinker) photo server for the optical chamber
// Paper (Bagian 3): flash LED GPIO 4 off, light only from the LED strip; resolution, exposure,
// gain and white balance locked since test T1; three photos per sample sent over Wi-Fi to the
// laptop with a file name from the batch code.
// Use: http://<ip>/capture?batch=<batch code>&n=<1..3>  -> one fresh JPEG, file name <batch>_<n>.jpg
// The laptop asks three times per sample. Photos are on command only: the paper's minute 10/20/30
// times (T3) are when a sample is pipetted out, not when the camera shoots by itself.

#include "esp_camera.h"
#include <WiFi.h>
#include <WebServer.h>
#include "secrets.h"  // copy secrets.h.example to secrets.h and fill in; secrets.h is git-ignored

// ---- Locked camera settings: tune once at T1, then never change (paper) ----
const framesize_t FRAME_SIZE = FRAMESIZE_SVGA;  // ASSUMED: 800x600; paper only needs a 100x100 px area in the vial centre
const int JPEG_QUALITY = 10;                    // ASSUMED: 0-63, lower = better; low compression keeps colour means stable
const int AEC_VALUE = 300;                      // ASSUMED: manual exposure 0-1200; set at T1
const int AGC_GAIN = 0;                         // ASSUMED: manual gain 0-30 (0 = 1x, least noise); set at T1
const int WB_MODE = 3;                          // ASSUMED: fixed white balance preset 1-4 (3 = office); set at T1

const int PIN_FLASH_LED = 4;  // paper: program turns the flash LED (GPIO 4) off

// AI-Thinker ESP32-CAM camera pins. ASSUMED: standard AI-Thinker map (Espressif camera_pins.h);
// the paper names the AI-Thinker board (27 x 40.5 mm) but lists no camera pins (they are fixed on the board).
#define PWDN_GPIO_NUM 32
#define RESET_GPIO_NUM -1
#define XCLK_GPIO_NUM 0
#define SIOD_GPIO_NUM 26
#define SIOC_GPIO_NUM 27
#define Y9_GPIO_NUM 35
#define Y8_GPIO_NUM 34
#define Y7_GPIO_NUM 39
#define Y6_GPIO_NUM 36
#define Y5_GPIO_NUM 21
#define Y4_GPIO_NUM 19
#define Y3_GPIO_NUM 18
#define Y2_GPIO_NUM 5
#define VSYNC_GPIO_NUM 25
#define HREF_GPIO_NUM 23
#define PCLK_GPIO_NUM 22

WebServer server(80);  // ASSUMED: plain HTTP on port 80, laptop pulls photos (paper says only "via Wi-Fi ke laptop")

bool initCamera() {
  camera_config_t c = {};
  c.ledc_channel = LEDC_CHANNEL_0;
  c.ledc_timer = LEDC_TIMER_0;
  c.pin_d0 = Y2_GPIO_NUM;
  c.pin_d1 = Y3_GPIO_NUM;
  c.pin_d2 = Y4_GPIO_NUM;
  c.pin_d3 = Y5_GPIO_NUM;
  c.pin_d4 = Y6_GPIO_NUM;
  c.pin_d5 = Y7_GPIO_NUM;
  c.pin_d6 = Y8_GPIO_NUM;
  c.pin_d7 = Y9_GPIO_NUM;
  c.pin_xclk = XCLK_GPIO_NUM;
  c.pin_pclk = PCLK_GPIO_NUM;
  c.pin_vsync = VSYNC_GPIO_NUM;
  c.pin_href = HREF_GPIO_NUM;
  c.pin_sccb_sda = SIOD_GPIO_NUM;
  c.pin_sccb_scl = SIOC_GPIO_NUM;
  c.pin_pwdn = PWDN_GPIO_NUM;
  c.pin_reset = RESET_GPIO_NUM;
  c.xclk_freq_hz = 20000000;
  c.pixel_format = PIXFORMAT_JPEG;
  c.frame_size = FRAME_SIZE;
  c.jpeg_quality = JPEG_QUALITY;
  c.fb_count = 1;
  c.fb_location = CAMERA_FB_IN_PSRAM;
  c.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
  if (esp_camera_init(&c) != ESP_OK) return false;

  sensor_t *s = esp_camera_sensor_get();
  s->set_wb_mode(s, WB_MODE);   // fixed preset, turns auto white balance off
  s->set_whitebal(s, 0);
  s->set_awb_gain(s, 0);
  s->set_exposure_ctrl(s, 0);   // auto exposure off
  s->set_aec2(s, 0);
  s->set_aec_value(s, AEC_VALUE);
  s->set_gain_ctrl(s, 0);       // auto gain off
  s->set_agc_gain(s, AGC_GAIN);
  return true;
}

// Batch code comes from the laptop: keep only safe file-name characters.
String cleanName(String in) {
  String out;
  for (char ch : in) {
    if (isalnum((unsigned char)ch) || ch == '-' || ch == '_') out += ch;
    if (out.length() >= 40) break;
  }
  return out.length() ? out : String("foto");
}

void handleCapture() {
  // With one frame buffer, the frame already waiting may be old (taken before the vial door closed): drop it.
  camera_fb_t *fb = esp_camera_fb_get();
  if (fb) esp_camera_fb_return(fb);
  fb = esp_camera_fb_get();
  if (!fb) {
    server.send(500, "text/plain", "capture failed");
    return;
  }
  String name = cleanName(server.arg("batch"));
  if (server.hasArg("n")) name += "_" + cleanName(server.arg("n"));
  server.sendHeader("Content-Disposition", "inline; filename=" + name + ".jpg");
  server.setContentLength(fb->len);
  server.send(200, "image/jpeg", "");
  server.client().write(fb->buf, fb->len);
  esp_camera_fb_return(fb);
}

void setup() {
  pinMode(PIN_FLASH_LED, OUTPUT);
  digitalWrite(PIN_FLASH_LED, LOW);
  Serial.begin(115200);  // ASSUMED: debug only (shows IP); needs the programming board attached

  if (!initCamera()) {
    Serial.println("ERROR: camera init failed");
    while (true) delay(1000);
  }

  WiFi.mode(WIFI_STA);  // ASSUMED: joins an existing Wi-Fi network (laptop on the same network)
  WiFi.setSleep(false);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) delay(500);
  Serial.print("Ready: http://");
  Serial.print(WiFi.localIP());
  Serial.println("/capture?batch=<code>&n=<1..3>");

  server.on("/capture", handleCapture);
  server.begin();
}

void loop() {
  server.handleClient();
}
