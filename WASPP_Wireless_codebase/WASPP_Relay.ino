/*
 * WASPP Feather firmware
 * ---------------------
 * The Feather is the communication bridge between the Base Station and Drone Pi:
 * --------- Drone PI <---> Feather < - - - > Base Station
 *                    (USB)           (LoRa)
 *
 * It also reads its locally attached environmental sensors and transmits those
 * readings as JSON telemetry packets when live sensor mode is enabled.
 *
 * Nathan Bartley - NSF NCAR-UCAR CISL Interxn 2026
 */

#include <SPI.h>
#include <RH_RF95.h>
#include <ArduinoJson.h>
#include <Wire.h>

//-------------------- sensors ----
#include <Adafruit_Sensor.h>
#include <Adafruit_TMP117.h> // dont care
#include <Adafruit_LTR390.h> // dont care 
#include <Adafruit_BME680.h> // neeed RH, TMP, and GAS
#include <Adafruit_PM25AQI.h> // important

// -------------------- LoRa Config --------------------
// Hardware pin assignments for the RFM95 LoRa radio connected to the RP2040
// Feather. RF95_FREQ must match the base station radio configuration.

#define RFM95_CS   16
#define RFM95_INT  21
#define RFM95_RST  17
#define RF95_FREQ  915.0

RH_RF95 rf95(RFM95_CS, RFM95_INT);

//---------------------- Sensor Config ---------------------
// Sensor timing and conversion configuration. Values are stored globally so the
// latest successful reading can be placed in a telemetry packet at any time.
#define BME680_UPDATE_MS 2000

#define SEALEVELPRESSURE_HPA 1013.25
#define SENSOR_UPDATES_MS 3000;
#define LTR390_SETTLE_MS 120
#define LTR390_UPDATE_MS 2000

Adafruit_TMP117 tmp117;
Adafruit_LTR390 ltr390;
Adafruit_BME680 bme680;
Adafruit_PM25AQI pm25aqi;

// Each flag records whether a sensor responded during setup. A disconnected
// sensor is skipped later instead of repeatedly attempting failed reads.
bool pm25aqi_connected = false;
bool tmp117_connected = false;
bool ltr390_connected = false;
bool bme680_connected = false;

// Live mode causes periodic SENSOR packets. It is controlled by LoRa commands
// and paused during Drone Pi command/ACK relays to avoid radio collisions.
bool live_sensor_mode = false;
unsigned long live_sensor_period_ms = 3000;
unsigned long last_sensor_send_ms = 0;
unsigned long ltr390_state_start_ms = 0;
unsigned long last_ltr390_update_ms = 0;
unsigned long last_pm25aqi_update_ms = 0;

// The LTR390 cannot immediately return a valid value after switching between
// UV and ambient-light modes. This state machine waits without blocking loop().
// (Could drop this we arent really using this sensor)
enum Ltr390State {
  LTR_IDLE,
  LTR_WAIT_UVS,
  LTR_WAIT_ALS
};

Ltr390State ltr390_state = LTR_IDLE;

uint32_t sensor_packet_id = 1;

//--------------- Global Sensor Values Stuff ------------------
// Cached readings and validity flags. A field is included in a SENSOR packet
// only after its sensor has supplied at least one valid value.
//copy similar structure when adding new sensors
float tmp117_c = NAN;

float bme_t = NAN;
float bme_rh = NAN;
float bme_p = NAN;
float bme_g = NAN;

uint32_t uvs = 0;
uint32_t als = 0;

float pm25 = NAN;

bool tmp117_valid = false;
bool bme_valid = false;
bool ltr390_valid = false;
bool pm25aqi_valid = false;

unsigned long tmp117_update_ms = 0;
unsigned long bme680_update_ms = 0;
unsigned long ltr390_update_ms = 0;
unsigned long pm25aqi_update_ms = 0;

// -------------------- Packet Config --------------------
// IDs and system name used to validate packet origin/destination. All platforms
// must use the same SYS_ID for packets to be accepted.

const char* SYS_ID = "demo";  // Change to WASPP on all platforms
const char* FEATHER_ID = "FTR";
const char* BASE_ID = "BS";
const char* DRONEPI_ID = "DrPi";

// ------------------- SERIAL Config ----------------
// USB serial is line-delimited JSON. This buffer accumulates bytes from Drone Pi
// until a newline marks a complete packet.
char usb_rx_buffer[512];
size_t usb_rx_index = 0;

// -------------------- DrPi ACK Relay State --------------------
// A Drone Pi response is held briefly before retransmission so the base station
// has time to return its LoRa radio to receive mode after sending a command.

bool waiting_for_drpi_ack = false;

char pending_drpi_relay[512];
bool drpi_relay_pending = false;

unsigned long drpi_command_rx_ms = 0;
unsigned long drpi_relay_send_at_ms = 0;

#define DRPI_ACK_TURNAROUND_MS 200
#define DRPI_ACK_TIMEOUT_MS    3000

// -------------------- Setup --------------------
/**
 * Initializes USB serial, I2C, LoRa, and all attached sensors. (get more 
 * sensor code from Mesonet if needed)
 * The short Serial wait supports hosts that need time to open the USB port,
 * but does not prevent standalone operation indefinitely.
 */
void setup() {
  Serial.begin(115200);

  unsigned long start = millis();
  while (!Serial && millis() - start < 3000) {
    delay(10);
  }

  Wire.begin();

  init_lora();
  init_sensors();

  // Serial.println("Ready");
}

// -------------------- Main Loop --------------------

/**
 * Runs the cooperative, non-blocking scheduler.
 * Each pass checks both communications paths, refreshes sensors when due,
 * resolves Drone Pi relay timing, and sends periodic telemetry if enabled.
 */
void loop() {
  receive_packet();
  receive_usb_packet();

  update_sensors_nonblocking();

  check_drpi_ack_timeout();
  handle_pending_drpi_relay();

  handle_live_sensor_mode();
}

// -------------------- LoRa Init --------------------

/**
 * Resets and configures the RFM95 radio.
 * Radio modem settings must remain compatible with the Raspberry Pi base
 * station: spreading factor 7, 125 kHz bandwidth, and coding rate 4/5.
 */
void init_lora() {
  pinMode(RFM95_RST, OUTPUT);

  digitalWrite(RFM95_RST, HIGH);
  delay(10);
  digitalWrite(RFM95_RST, LOW);
  delay(10);
  digitalWrite(RFM95_RST, HIGH);
  delay(10);

  if (!rf95.init()) {
    Serial.println("ERROR: RFM95 init failed");
    while (1);
  }

  if (!rf95.setFrequency(RF95_FREQ)) {
    Serial.println("ERROR: RFM95 frequency failed");
    while (1);
  }

  // Matches Pi: SF7, BW125kHz, CR4/5
  rf95.setModemConfig(RH_RF95::Bw125Cr45Sf128);
  rf95.setTxPower(23, false);

  // Serial.println("LoRa initialized");
}
// ___--_--_--_- sensor inint -----
/**
 * Probes each I2C sensor and applies its operating configuration.
 * Failed probes are non-fatal: their connected flag remains false and the
 * rest of the system continues running.
 */
void init_sensors() {
  delay(3000);  // PMSA003I needs time to boot

  if (!pm25aqi.begin_I2C()) {
    // Serial.println("PM2.5 sensor not found");
    pm25aqi_connected = false;
  } else {
    // Serial.println("PM2.5 sensor found");
    pm25aqi_connected = true;
  }
  if (tmp117.begin()) {
    tmp117_connected = true;
    // Serial.println("TMP117 initialized");
  } else {
    tmp117_connected = false;
    // Serial.println("TMP117 not found");
  }

  if (ltr390.begin()) {
    ltr390_connected = true;

    ltr390.setMode(LTR390_MODE_UVS);
    ltr390.setGain(LTR390_GAIN_3);
    ltr390.setResolution(LTR390_RESOLUTION_16BIT);

    // Serial.println("LTR390 initialized");
  } else {
    ltr390_connected = false;
    // Serial.println("LTR390 not found");
  }

  if (bme680.begin()) {
    bme680_connected = true;

    bme680.setTemperatureOversampling(BME680_OS_8X);
    bme680.setHumidityOversampling(BME680_OS_2X);
    bme680.setPressureOversampling(BME680_OS_4X);
    bme680.setIIRFilterSize(BME680_FILTER_SIZE_3);
    bme680.setGasHeater(320, 150);

    // Serial.println("BME680 initialized");
  } else {
    bme680_connected = false;
    // Serial.println("BME680 not found");
  }
}
// -------------------- Receive Packets --------------------

/**
 * Reads newline-delimited JSON arriving from the Drone Pi over USB serial.
 * Carriage returns are ignored so both LF and CRLF line endings work. If the
 * buffer fills before a newline arrives, the partial packet is discarded.
 */
void receive_usb_packet() {
  //Receives packets from drone Pi
  while (Serial.available() > 0) {
    char c = (char)Serial.read();

    if (c == '\r') {
      continue;
    }

    if (c == '\n') {
      usb_rx_buffer[usb_rx_index] = '\0';

      if (usb_rx_index > 0) {
        handle_drone_pi_packet(usb_rx_buffer);
      }

      usb_rx_index = 0;
      continue;
    }

    if (usb_rx_index < sizeof(usb_rx_buffer) - 1) {
      usb_rx_buffer[usb_rx_index++] = c;
    } else {
      usb_rx_index = 0;
    }
  }
}

//    Receive packets from base station over LoRa
/**
 * Receives at most one LoRa packet per loop iteration and passes its
 * null-terminated payload to the LoRa command handler.
 */
void receive_packet() {
  if (!rf95.available()) {
    return;
  }

  uint8_t buf[RH_RF95_MAX_MESSAGE_LEN + 1];
  uint8_t len = RH_RF95_MAX_MESSAGE_LEN;

  if (!rf95.recv(buf, &len)) {
    // Serial.println("RX failed");
    return;
  }

  buf[len] = '\0';

  // Serial.print("RX: ");
  // Serial.println((char*)buf);

  handle_packet((char*)buf);
}

// -------------------- Packet Handler --------------------
/**
 * Validates a JSON packet received from Drone Pi.
 * STT packets are forwarded immediately. Valid Drone Pi ACK packets are copied
 * into a pending relay buffer and sent after the configured turnaround delay.
 *
 * @param raw Null-terminated JSON line received over USB serial.
 */
void handle_drone_pi_packet(const char* raw) {
  StaticJsonDocument<512> doc;

  DeserializationError err = deserializeJson(doc, raw);
  if (err) {
    // Ignore malformed serial data.
    return;
  }

  const char* sys = doc["sys"] | "";
  const char* type = doc["t"] | "";
  const char* sender_id = doc["sid"] | "";

  // Only relay valid ACK packets generated by the Drone Pi.
  if (strcmp(sys, SYS_ID) != 0) {
    return;
  }

  if (strcmp(type, "STT") == 0) {
     send_packet(raw);
      return;
  }
  if (strcmp(type, "ACK") != 0) {
    return;
  }

  if (strcmp(sender_id, DRONEPI_ID) != 0) {
    return;
  }

  strncpy(pending_drpi_relay, raw, sizeof(pending_drpi_relay) - 1);
  pending_drpi_relay[sizeof(pending_drpi_relay) - 1] = '\0';

  drpi_relay_send_at_ms = drpi_command_rx_ms + DRPI_ACK_TURNAROUND_MS;
  drpi_relay_pending = true;
}

/**
 * Sends a previously saved Drone Pi ACK once the turnaround timer expires.
 * This avoids transmitting while the base station is still switching from
 * transmit mode to receive mode.
 */
void handle_pending_drpi_relay() {
  if (!drpi_relay_pending) {
    return;
  }

  unsigned long now = millis();

  // Wait until the base station should safely be listening.
  if (now < drpi_relay_send_at_ms) {
    return;
  }

  send_packet(pending_drpi_relay);

  drpi_relay_pending = false;
  waiting_for_drpi_ack = false;
}

/**
 * Cancels a pending Drone Pi response window after DRPI_ACK_TIMEOUT_MS.
 * This prevents live sensor mode from remaining blocked forever if Drone Pi
 * does not return an ACK.
 */
void check_drpi_ack_timeout() {
  if (!waiting_for_drpi_ack) {
    return;
  }

  unsigned long now = millis();

  if (now - drpi_command_rx_ms > DRPI_ACK_TIMEOUT_MS) {
    waiting_for_drpi_ack = false;
    drpi_relay_pending = false;

    Serial.println("DrPi ACK timeout");
  }
}

/**
 * Validates an incoming LoRa command and routes it either to Drone Pi or to
 * a Feather-local command handler.
 *
 * @param raw Null-terminated JSON packet received through LoRa.
 */
void handle_packet(const char* raw) {
  StaticJsonDocument<192> doc;

  DeserializationError err = deserializeJson(doc, raw);
  if (err) {
    // Serial.println("Ignored: invalid JSON");
    return;
  }

  const char* sys = doc["sys"] | "";
  const char* type = doc["t"] | "";
  const char* cmd = doc["cmd"] | "";
  const char* to = doc["to"] | "";
  uint32_t seq = doc["seq"] | 0;


  if (strcmp(sys, SYS_ID) != 0) {
    //Serial.println("Ignored: wrong sys");
    return;
  }

  if (strcmp(type, "CMD") != 0) {
    // Serial.println("Ignored: not CMD");
    return;
  }

  if (strcmp(to, DRONEPI_ID) == 0) {
    handle_live_stop();
    forward_to_drpi(raw);
    return;
  }

  dispatch_command(seq, cmd);
}

/**
 * Relays a base-station command to Drone Pi unchanged over USB serial and
 * begins the timed window in which a Drone Pi ACK is expected.
 */
void forward_to_drpi(const char* raw) {
  // Mark the radio path as reserved for the Drone Pi response.
  waiting_for_drpi_ack = true;
  drpi_command_rx_ms = millis();

  // Forward the original command unchanged over USB.
  Serial.println(raw);
}
// -------------------- Command Dispatcher --------------------

/**
 * Handles commands addressed to the Feather itself.
 *
 * @param seq Base-station sequence number, returned in any ACK.
 * @param cmd Command string parsed from the incoming JSON packet.
 */
void dispatch_command(uint32_t seq, const char* cmd) {
  if (strcmp(cmd, "take_sample") == 0) {
    handle_live_stop();
    // handle_take_sample(seq);
  }

  else if (strcmp(cmd, "status") == 0) {
    handle_live_stop();
    // handle_pi_status(seq);
  }

  else if (strcmp(cmd, "live_start") == 0) {
    handle_live_start(seq);
  }

  else {
    send_ack(seq, cmd, false, "unknown command");
  }
}

//----------------- DrPi command placeholders ---------
// void handle_take_sample(uint32_t seq) {
//   // Serial.println("Command: take_sample");

//   // Relay take_sample command over USB
//   send_ack(seq, "take_sample", true, "cmd_received");
//   // WAIT FOR ACK FROM DrPi Before sending Ack
//   //send_ack(seq, "take_sample", true, "sample_taken");
// }

// void handle_pi_status(uint32_t seq) {
//   Serial.println("Command: pi_status");

//   send_ack(seq, "pi_status", true, "Status Request Received");

//   delay(100);  // gives Pi time to return to RX after the ACK

//   // Wait for status json from DrPi
//   //send_status(seq, .......)
// }

// -------------------- Feather Sensor Packet Handling --------------------
/**
 * Rounds a floating-point sensor value to one decimal place before telemetry.
 * This reduces packet size and makes the base-station display easier to read.
 */
float round1(float value) {
  return round(value * 10.0) / 10.0;
}

/**
 * Enables periodic environmental telemetry and confirms activation to the
 * base station using the originating command sequence number.
 */
void handle_live_start(uint32_t seq) {

  live_sensor_period_ms = SENSOR_UPDATES_MS;
  live_sensor_mode = true;
  last_sensor_send_ms = millis();

  delay(100);

  send_ack(seq, "live_start", true, "live mode on");
}

/**
 * Disables periodic Feather sensor telemetry. This is called before commands
 * that require radio time for a Drone Pi request/response exchange.
 */
void handle_live_stop() {
  live_sensor_mode = false;
  // send_ack(seq, "live_stop", true, "live mode off");
}

/**
 * Builds and transmits the Feather SENSOR JSON packet.
 * Only readings marked valid are serialized, allowing partial telemetry when
 * one or more sensors are absent or have not produced a successful reading.
 */
void send_sensor_packet() {
  StaticJsonDocument<384> doc;
  char packet[384];

  doc["sys"] = SYS_ID;
  doc["t"] = "SENSOR";
  doc["sid"] = FEATHER_ID;
  doc["id"] = sensor_packet_id++;
  doc["ms"] = millis();

  if (tmp117_valid) {
    doc["tmp117_c"] = tmp117_c;
  }

  if (bme_valid) {
    doc["bme_t"] = bme_t;
    doc["bme_rh"] = bme_rh;
    doc["bme_p"] = bme_p;
    doc["bme_g"] = bme_g;
  }

  if (ltr390_valid) {
    doc["uvs"] = uvs;
    doc["als"] = als;
  }
  
  if (pm25aqi_valid) {
    doc["pm25"] = pm25;
  }
  size_t n = serializeJson(doc, packet, sizeof(packet));

  if (n == 0 || n >= sizeof(packet)) {
    Serial.println("ERROR: SENSOR packet overflow");
    return;
  }
  send_packet(packet);
}

//---------- Local Sensor Updating ----------
#define TMP117_UPDATE_MS 1000

/**
 * Invokes each sensor updater. Individual updaters use elapsed-time checks or
 * a state machine, so this function does not intentionally wait for sensors.
 */
void update_sensors_nonblocking() {
  update_tmp117();
  update_bme680();
  update_ltr390();
  update_pm25aqi();
}

/**
 * Refreshes the TMP117 temperature cache no more often than TMP117_UPDATE_MS.
 */
void update_tmp117() {
  if (!tmp117_connected) {
    return;
  }

  unsigned long now = millis();

  if (now - tmp117_update_ms < TMP117_UPDATE_MS) {
    return;
  }

  tmp117_update_ms = now;

  sensors_event_t temp;
  tmp117.getEvent(&temp);

  tmp117_c = round1(temp.temperature);
  tmp117_valid = true;
}


unsigned long last_bme680_update_ms = 0;

/**
 * Refreshes BME680 temperature, humidity, pressure, and gas-resistance caches.
 * BME pressure is converted from Pa to hPa; gas resistance is converted from
 * ohms to kilo-ohms before one-decimal rounding.
 */
void update_bme680() {
  if (!bme680_connected) {
    return;
  }

  unsigned long now = millis();

  if (now - last_bme680_update_ms < BME680_UPDATE_MS) {
    return;
  }

  last_bme680_update_ms = now;

  if (bme680.performReading()) {
    bme_t = round1(bme680.temperature);
    bme_rh = round1(bme680.humidity);
    bme_p = round1(bme680.pressure / 100.0);
    bme_g = round1(bme680.gas_resistance / 1000.0);
    bme_valid = true;
  } else {
    bme_valid = false;
  }
}
/**
 * Advances the non-blocking LTR390 measurement state machine:
 * UVS mode -> wait -> read UVS -> ALS mode -> wait -> read ALS.
 * (Again, probably not using this sensor)
 */
void update_ltr390() {
  if (!ltr390_connected) {
    return;
  }

  unsigned long now = millis();

  switch (ltr390_state) {
    case LTR_IDLE:
      if (now - ltr390_update_ms >= LTR390_UPDATE_MS) {
        ltr390.setMode(LTR390_MODE_UVS);
        ltr390_state_start_ms = now;
        ltr390_state = LTR_WAIT_UVS;
      }
      break;

    case LTR_WAIT_UVS:
      if (now - ltr390_state_start_ms >= LTR390_SETTLE_MS) {
        uvs = ltr390.readUVS();

        ltr390.setMode(LTR390_MODE_ALS);
        ltr390_state_start_ms = now;
        ltr390_state = LTR_WAIT_ALS;
      }
      break;

    case LTR_WAIT_ALS:
      if (now - ltr390_state_start_ms >= LTR390_SETTLE_MS) {
        als = ltr390.readALS();

        ltr390_valid = true;
        ltr390_update_ms = now;
        ltr390_state = LTR_IDLE;
      }
      break;
  }
}
/**
 * Reads the PMSA003I/PM2.5 sensor when its update interval has elapsed.
 * The transmitted value is pm25_env, the environmental PM2.5 concentration
 * reported by the Adafruit driver.
 */
void update_pm25aqi() {
  if (!pm25aqi_connected) {
    return;
  }

  unsigned long now = millis();

  if (now - last_pm25aqi_update_ms < pm25aqi_update_ms) {
    return;
  }

  last_pm25aqi_update_ms = now;

  PM25_AQI_Data pmData;


  if (pm25aqi_connected && pm25aqi.read(&pmData)) {
    pm25 = pmData.pm25_env;
    pm25aqi_valid = true;
  }
  else {
    pm25aqi_valid = false;
  }
}
// -------------------- ACK Helpers --------------------

/**
 * Constructs and transmits a Feather-originated ACK packet.
 *
 * @param seq Sequence number from the command being acknowledged.
 * @param cmd Command name being acknowledged.
 * @param ok Success flag encoded as 1 or 0 in JSON.
 * @param msg Short human-readable result message.
 */
void send_ack(uint32_t seq, const char* cmd, bool ok, const char* msg) {
  StaticJsonDocument<192> doc;
  char packet[192];

  doc["sys"] = SYS_ID;
  doc["t"] = "ACK";
  doc["sid"] = FEATHER_ID;
  doc["seq"] = seq;
  doc["cmd"] = cmd;
  doc["ok"] = ok ? 1 : 0;
  doc["msg"] = msg;

  size_t n = serializeJson(doc, packet, sizeof(packet));

  if (n == 0 || n >= sizeof(packet)) {
    Serial.println("ERROR: ACK overflow");
    return;
  }

  send_packet(packet);
}

/**
 * Sends periodic sensor telemetry while live mode is active. Transmission is
 * suppressed whenever a Drone Pi command or delayed response relay is active.
 */
void handle_live_sensor_mode() {
  if (!live_sensor_mode) {
    return;
  }

  // Do not transmit periodic telemetry while a DrPi command/ACK exchange
  // is in progress.
  if (waiting_for_drpi_ack || drpi_relay_pending) {
    return;
  }

  unsigned long now = millis();

  if (now - last_sensor_send_ms >= live_sensor_period_ms) {
    last_sensor_send_ms = now;
    send_sensor_packet();
  }
}

/**
 * Sends a null-terminated JSON string over LoRa and blocks only until the
 * RFM95 hardware reports that this packet has finished transmitting.
 */
void send_packet(const char* packet) {
  // Serial.print("TX: ");
  // Serial.println(packet);
  // delay(150);
  rf95.send((uint8_t*)packet, strlen(packet));
  rf95.waitPacketSent();
}