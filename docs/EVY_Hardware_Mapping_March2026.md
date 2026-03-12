# EVY lilEVY — Physical Hardware Mapping Analysis
*March 2026*

---

## TL;DR

The code assumes one specific hardware stack but maps it incorrectly in several places. The GSM driver will work on the right module but uses the wrong library for the right module. The LoRa driver has zero physical wiring — it is 100% simulated with commented-out GPIO code. GPS, solar monitoring, and battery telemetry exist only as stubbed return values. The docker compose device mapping has a security hole. Nothing about the LoRa HAT's actual SPI chip-select wiring is handled correctly.

---

## 1. GSM HAT

### What the code assumes

- Device path: `/dev/ttyUSB0`
- Baud rate: `115200`
- Library: **Gammu** (`python-gammu`)
- Fallback: raw AT commands over `serial` via `SerialGSMDriver`

### The hardware reality

The repo mentions "GSM HAT" but the SIM800 series (SIM800L, SIM800C) — the most common "GSM HAT" — is **2G only**. In the US, T-Mobile shut down 2G in 2022. AT&T shut it down in 2017. If lilEVY is deploying on US carriers, a SIM800-based HAT is dead on arrival.

The correct module for this use case on Pi 4 is the **Waveshare SIM7600G-H 4G HAT** (or region-specific variant like SIM7600NA-H for North America). It supports 4G/3G/2G fallback, has onboard GNSS (GPS/BeiDou/Glonass/Galileo), and includes a TF card slot. This is almost certainly what the BOM intends, but the code doesn't say so explicitly anywhere.

### Gammu vs AT commands

Gammu works with SIM7600 series modules but has inconsistencies. The `SerialGSMDriver` (direct AT commands) is actually the more reliable path for the SIM7600 series — Gammu adds complexity without adding value here. The `Ircama/sim800l-gsm-module` Python library is excellent for AT-command-based control but is named for SIM800 and will need AT command adjustments for SIM7600 (the commands are largely compatible but not identical).

### Device path issues

The SIM7600G-H HAT registers **multiple serial ports** on the Pi:

- `/dev/ttyUSB0` — AT command interface (correct for SMS)
- `/dev/ttyUSB1` — GPS NMEA data stream
- `/dev/ttyUSB2` — diagnostic/modem
- `/dev/ttyUSB3` — audio

The code assumes `/dev/ttyUSB0` for AT commands, which is correct for the primary interface. However, the compose file maps only `/dev/ttyUSB0` in the `devices:` block. If GPS is ever pulled from the module (see section 3), `/dev/ttyUSB1` also needs to be mapped and passed into the container.

### The Gammu config issue

`GSMDriver.initialize()` calls `self.state_machine.ReadConfig(config)` with a dict. Gammu's Python bindings actually expect the config to be loaded from a `.gammurc` file or passed via `ReadConfig(Filename=...)`. Passing a raw dict to `ReadConfig()` will raise a TypeError at runtime. This is a silent integration bug — the fallback to `SerialGSMDriver` will catch it, but Gammu will never successfully initialize.

### North America note

If deploying in the US, the correct HAT is the **SIM7600NA-H** (North American bands), not the global SIM7600G-H. The global variant supports different LTE bands and may have weak signal on US carriers. This is a procurement decision, not a code decision, but it needs to be in the BOM and the deploy docs.

---

## 2. LoRa HAT

### What the code assumes

```python
self.hardware_simulated = True
self.lora_device = None
```

Virtually everything. The `_initialize_hardware()` method has the correct skeleton but every hardware call is commented out:

```python
# import spidev
# import RPi.GPIO as GPIO
# self.spi = spidev.SpiDev()
# self.spi.open(0, 0)
# GPIO.setmode(GPIO.BCM)
```

So the physical wiring, SPI configuration, GPIO interrupt setup, register writes — none of it runs. This is not a partial implementation. It is a complete stub.

### The hardware reality: Dragino LoRa/GPS HAT

The most common Pi LoRa HAT used for this type of deployment is the **Dragino LoRa/GPS HAT** (SX1276/SX1278 + L80 GPS, MTK MT3339). It is what the repo appears to be targeting based on the frequency defaults (`433.0 MHz` in config, though 915 MHz is correct for US ISM band — more on that below).

#### The Dragino SPI chip-select defect

This is a known hardware issue. The Dragino HAT wires SPI chip select to **GPIO 25 (pin 22)** instead of the standard **CE0 (GPIO 8, pin 24)**. The Pi's SPI kernel driver controls CE0 automatically; GPIO 25 requires software-controlled chip select. If you use `spidev.SpiDev().open(0, 0)` as the commented code suggests, the LoRa module will never respond because the chip select line is on the wrong pin.

The correct setup for Dragino:
```python
import spidev
import RPi.GPIO as GPIO

CS_PIN = 25   # GPIO 25, not CE0
DIO0_PIN = 4  # GPIO 4 — interrupt / TX done / RX done
RST_PIN = 17  # GPIO 17 — reset

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 5000000

GPIO.setmode(GPIO.BCM)
GPIO.setup(CS_PIN, GPIO.OUT)
GPIO.setup(DIO0_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(RST_PIN, GPIO.OUT)

# Manual chip select on every transaction:
GPIO.output(CS_PIN, GPIO.LOW)
# ... SPI transfer ...
GPIO.output(CS_PIN, GPIO.HIGH)
```

The code has `self.spi.open(0, 0)` in the comment — this will fail silently or return garbage because CE0 is not connected to the LoRa chip on Dragino hardware.

#### Frequency is wrong for US deployment

The code sets `self.frequency = 433.0` MHz. In the United States, the unlicensed ISM band for LoRa is **902–928 MHz** (typically 915 MHz center). 433 MHz is the EU/Asia band. Transmitting LoRa at 433 MHz in the US is an FCC violation for this use case. This needs to be a deployment-region config variable:

```python
LORA_FREQUENCY_MHZ = 915.0  # US/AU
# LORA_FREQUENCY_MHZ = 868.0  # EU
# LORA_FREQUENCY_MHZ = 433.0  # Asia/other
```

#### Required packages not in requirements.txt

Neither `spidev` nor `RPi.GPIO` is in `requirements.txt`. On a Pi, `RPi.GPIO` also requires enabling SPI in `raspi-config` (`dtparam=spi=on` in `/boot/config.txt`) — this is a first-boot system configuration step that has no automation in the deploy scripts.

The correct additions to `requirements.txt` for the LoRa HAT:
```
spidev>=3.6
RPi.GPIO>=0.7.1
```

And `pyLoRa` (PyPI) or `pySX127x` are the best-supported Python LoRa libraries for SX1276 on Pi. The `pyLoRa` package wraps `spidev` and `RPi.GPIO` and handles register-level SX1276 configuration.

#### docker-compose LoRa device mapping

The `node-communication` service (which hosts `lora_radio_service.py`) has **no device mappings at all** in the compose file. SPI and GPIO access from inside a Docker container on Pi requires:

```yaml
node-communication:
  devices:
    - /dev/spidev0.0:/dev/spidev0.0
  volumes:
    - /sys/class/gpio:/sys/class/gpio
  privileged: true   # or cap_add: [SYS_RAWIO]
```

Without these, the container cannot access SPI or GPIO regardless of how the Python code is written.

---

## 3. GPS

### Current state

`_get_node_position()` returns `None` unconditionally:
```python
async def _get_node_position(self) -> Optional[Dict[str, float]]:
    # This would get actual GPS coordinates
    # For now, return None (no GPS module)
    return None
```

`_get_node_capabilities()` has `"gps_position": False`.

### The hardware opportunity you are missing

If the HAT is the **Dragino LoRa/GPS HAT**, there is an **L80 GPS module (MTK MT3339) already on the board**. The GPS outputs standard NMEA sentences over `/dev/ttyAMA0` (Pi's hardware UART). This is free hardware that is completely unused.

If the HAT is the **Waveshare SIM7600G-H 4G HAT**, it also has integrated GNSS (GPS/BeiDou/Glonass/Galileo) accessible via AT commands on `/dev/ttyUSB1`.

GPS is not a nice-to-have. For a disaster response / off-grid node, GPS position enables:

- Node discovery in LoRa mesh (currently `position: None` in every discovery packet)
- Geographic routing (query from rural Kansas routes differently than query from Port-au-Prince)
- Timestamping without NTP (GPS provides precision time off-grid)
- Emergency dispatch with coordinates ("nearest hospital to my location")
- Node health reporting with deployment location

### GPS implementation

For Dragino L80 (hardware UART):
```python
import serial
import pynmea2  # pip install pynmea2

async def _get_node_position():
    with serial.Serial('/dev/ttyAMA0', 9600, timeout=1) as gps:
        line = gps.readline().decode('ascii', errors='replace')
        if line.startswith('$GPRMC') or line.startswith('$GPGGA'):
            msg = pynmea2.parse(line)
            return {'lat': msg.latitude, 'lon': msg.longitude}
```

For SIM7600 GNSS (AT command):
```
AT+CGPS=1       # enable GPS
AT+CGPSINFO     # get position
```

Add `pynmea2` to requirements.txt. Add `/dev/ttyAMA0` to the `node-communication` compose service devices. Disable the Pi's serial console first (`raspi-config` → Interface Options → Serial → No console, Yes hardware).

---

## 4. Solar & Battery

### Current state

`_get_battery_level()` returns a hardcoded `85.0`. Solar is mentioned in the compose environment (`NODE_TYPE=lilevy`) and in capability reporting (`"solar_power": True`), but there is no actual power monitoring anywhere in the codebase.

### What you need

A solar-powered Pi 4 needs:
- A **solar charge controller** with MPPT (e.g., Waveshare Solar Power Management HAT, or a Witty Pi, or PiJuice)
- A LiPo/LiFePO4 battery pack
- A way to read battery voltage and charge state from software

The most common Pi-compatible solution is the **Waveshare Solar Power Management HAT** or **PiJuice HAT**. Both expose battery state via I2C.

PiJuice example:
```python
from pijuice import PiJuice
pj = PiJuice(1, 0x14)

def get_battery_level():
    return pj.status.GetChargeLevel()['data']  # 0–100

def get_solar_input():
    return pj.status.GetIoVoltage()['data']  # mV
```

Without real battery telemetry:
- You cannot detect when the node is running on reserve (no sun for 2 days)
- You cannot throttle inference to conserve power
- You cannot send low-battery alerts to the mesh
- You cannot implement the power-aware query routing the architecture describes

The `NodeInfo` dataclass already has a `battery_level` field. The capability broadcast already includes `"solar_power": True`. The plumbing is there — the sensor read is just hardcoded.

Add to requirements.txt: `pijuice` (if using PiJuice) or `smbus2` (for raw I2C reads to Waveshare HAT).

---

## 5. HAT Stacking Problem

This is the biggest physical hardware issue that is never discussed in the docs.

**You cannot stack two HATs on a Pi using the standard HAT spec.**

The Pi has one 40-pin GPIO header. The HAT spec allocates a fixed I2C address (0x50) for each HAT's EEPROM. If you have a GSM HAT and a LoRa HAT both plugged into the same header, their EEPROMs collide and the Pi cannot boot cleanly. This is not a software problem — it is a physical constraint.

### Options for running GSM + LoRa simultaneously

**Option A (recommended): SIM7600 HAT via USB, LoRa via GPIO header**

The SIM7600G-H HAT connects to the Pi over USB (the USB port on the HAT, not GPIO) and exposes `/dev/ttyUSBx`. The LoRa HAT (Dragino or similar) sits on the GPIO header. Only one HAT is on the GPIO pins. This is the correct physical architecture.

This is also why the compose file maps `/dev/ttyUSB0` for GSM (USB path) and would need `/dev/spidev0.0` for LoRa (SPI path via GPIO) — they use entirely different buses.

**Option B: Combine them on one board**

The **Dragino LoRa/GPS HAT** has an onboard GPS. If you use SIM7600 via USB for GSM (Option A), you get GSM + LoRa + GPS on two physical connections (USB + GPIO header), no stacking conflict.

**Option C: Use a combined cellular + LoRa board**

RAK Wireless and similar vendors make single-board solutions with cellular + LoRa. More expensive but eliminates all stacking concerns.

### Current compose assumption

The compose file assumes GSM is on `/dev/ttyUSB0` (USB-connected, correct) but the `node-communication` service for LoRa has no device mappings (missing entirely). This is accidentally correct architecture — GSM over USB, LoRa over GPIO SPI — but the LoRa half is not wired up at all.

---

## 6. Summary: Hardware Mapping Gaps

| Hardware | Code Status | Critical Issues |
|---|---|---|
| GSM HAT (SIM7600) | 🟡 Partial | Gammu ReadConfig API call broken; GPS port `/dev/ttyUSB1` not mapped |
| GSM HAT (SIM800) | ❌ Wrong module | 2G dead on US carriers; do not use |
| LoRa HAT (Dragino SX1276) | ❌ 100% simulated | Wrong CS pin, wrong frequency (433 vs 915), no SPI/GPIO in container |
| LoRa frequency | ❌ Wrong | 433 MHz set; 915 MHz required for US |
| GPS (Dragino L80 or SIM7600 GNSS) | ❌ Stub only | Returns None; free hardware on both HATs is ignored |
| Battery telemetry | ❌ Stub only | Hardcoded 85%; no I2C sensor read |
| Solar monitoring | ❌ Missing | Mentioned in capabilities but no implementation |
| HAT stacking | ✅ Accidentally correct | GSM=USB, LoRa=GPIO (not stacked) — but undocumented |
| SPI enabled on Pi | ❌ Missing | `dtparam=spi=on` not in bootstrap/deploy scripts |
| Serial console disabled | ❌ Missing | Required for GPS UART; not in bootstrap scripts |
| LoRa container device access | ❌ Missing | No SPI/GPIO device mapping in compose for node-communication |
| spidev / RPi.GPIO in requirements | ❌ Missing | Not in requirements.txt |

---

## 7. Recommended Hardware BOM (lilEVY v1)

| Component | Recommended Part | Notes |
|---|---|---|
| Compute | Raspberry Pi 5 (4GB) | Better inference performance; Pi 4 works but is slower for BitNet |
| GSM/4G + GNSS | Waveshare SIM7600NA-H 4G HAT | North America; fallback 3G/2G; GNSS onboard; USB-connected |
| LoRa radio | Dragino LoRa/GPS HAT (SX1276, 915 MHz US version) | SPI-connected; onboard L80 GPS |
| Power management | Waveshare Solar Power HAT or PiJuice HAT | I2C battery telemetry; MPPT charging |
| Storage | 64GB A2-rated microSD or USB3 SSD | A2 rating for random I/O; SSD preferred for ChromaDB |
| Solar panel | 20W panel minimum (30W recommended) | Pi 5 + inference + radio = ~8–12W average |
| Battery | 10,000–20,000 mAh LiPo | 2–3 days reserve at average load |
| Enclosure | IP65-rated weatherproof box | GPS/LoRa antenna feedthrough required |
| Antennas | 4G LTE antenna (SIM7600 kit) + 915 MHz LoRa antenna (3 dBi) + GPS patch antenna | All external, weatherproof |

---

## 8. Immediate P0 Hardware Fixes

1. **Fix Gammu init call** — replace `ReadConfig(config_dict)` with `ReadConfig(Filename='/etc/gammurc')` and create a gammurc template in the repo. Or drop Gammu entirely and use `SerialGSMDriver` as the primary path.

2. **Add spidev and RPi.GPIO to requirements.txt** — required for any LoRa hardware work.

3. **Fix LoRa CS pin** — change from `spi.open(0, 0)` (CE0) to software-controlled CS on GPIO 25 for Dragino hardware, or add a `LORA_CS_PIN` env var.

4. **Fix LoRa frequency** — change default from `433.0` to `915.0` MHz for US deployment; parameterize by region env var.

5. **Add SPI device to node-communication compose service** — map `/dev/spidev0.0` and add GPIO access.

6. **Add `/dev/ttyUSB1` to sms-gateway compose service** — for GPS data from SIM7600.

7. **Add Pi boot config to deploy scripts** — `dtparam=spi=on`, serial console disable, SPI device permissions.

8. **Wire `_get_node_position()`** — read NMEA from `/dev/ttyAMA0` (Dragino L80) or AT+CGPSINFO (SIM7600); return actual coordinates.

9. **Wire `_get_battery_level()`** — read from PiJuice or Waveshare Solar HAT via I2C; real value required for power-aware routing.

---

*EVY Hardware Mapping Analysis | srex-dev | March 2026*
