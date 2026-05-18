# EVY First Hardware Purchase BOM

Reviewed: 2026-05-18

This BOM is for the first lilEVY bench node before field testing. The goal is one Raspberry Pi node that can run GSM SMS, local BitNet inference, local RAG, and validation reports. Mesh, solar, enclosure, OTA, and multi-node field packaging are intentionally later.

## Immediate Cart Verdict

Do not submit the pasted cart exactly as-is.

The useful parts are the LTE/GSM HAT, micro HDMI cable, UART adapter, and USB power meter. The risky or premature parts are the high-priced Raspberry Pi 5 16GB purchase, the non-official power supply, the PoE/NVMe HAT, and the raw UART LoRa module.

Pasted cart subtotal before tax was approximately `$633.24`.

## Buy Now For First Bench Node

| Item | Quantity | Recommendation | Why |
| --- | ---: | --- | --- |
| Raspberry Pi 5, 8GB or 16GB | 1 | Buy from Raspberry Pi Approved Reseller if possible. 8GB is the minimum target; 16GB is optional headroom. | The first EVY node needs Raspberry Pi 5 performance, GPIO/UART/SPI access, and enough RAM for BitNet plus local services. Do not overpay for 16GB unless schedule matters more than cost. |
| Official Raspberry Pi 27W USB-C power supply | 1 | Prefer official over the RasTech supply in the cart. | Bring-up should remove power variables. Raspberry Pi recommends a 5V/5A USB-C supply for Pi 5, and the official supply is specified at 5.1V/5A. |
| Official Raspberry Pi Active Cooler | 1 | Buy unless the selected case/HAT bundle has a known-good Pi 5 active cooler and does not block the LTE HAT. | BitNet benchmarks and sustained services need predictable thermals. |
| High-endurance microSD card, 128GB or larger | 2 | Add to cart. | One primary OS card and one spare/recovery card. This is missing from the pasted cart. |
| SIM7600G-H or SIM7600A-H 4G/LTE HAT | 1 | Keep the SIM7600G-H only after checking carrier bands; use SIM7600A-H if buying specifically for North America and it is available. | This is the right class of modem for GSM/LTE SMS validation. Waveshare lists SMS, GNSS, USB/UART AT-command support, and global/region variants. |
| SMS-capable SIM card and active plan | 1 | Add to cart or source from carrier. | Required for real inbound/outbound SMS tests. Data-only IoT SIMs may fail the SMS milestone. |
| Micro HDMI to HDMI cable | 1 | Keep. | Useful for first boot and recovery. |
| USB keyboard/mouse or known SSH setup | 1 | Add if not already available. | Needed for recovery if networking or SSH setup fails. |
| Ethernet cable | 1 | Add if not already available. | Wired network makes first setup simpler and more reliable. |
| USB to TTL UART adapter with FTDI chip | 1 | Keep, but set/verify 3.3V TTL before connecting to Pi GPIO. | Useful for serial console and modem/module debugging. Raspberry Pi UART/GPIO is 3.3V logic; avoid 5V on GPIO. |
| USB-C inline power meter | 1 | Keep if budget allows. | Useful for measuring boot, idle, BitNet inference, and modem transmit power draw. |

## Pasted Cart Line-Item Decisions

| Cart item | Price | Decision | Notes |
| --- | ---: | --- | --- |
| UANTIN 4K Micro HDMI to HDMI Cable 6FT | `$7.99` | Keep | Good bench accessory. |
| DSD TECH SH-U09C5 USB to TTL UART Converter Cable with FTDI | `$14.49` | Keep | Useful. Confirm 3.3V TTL wiring before Pi GPIO use. |
| Soldering iron + multimeter kit | `$42.99` | Optional | Fine if you need basic tools. A better standalone multimeter is preferable later, but this is enough for continuity/basic voltage checks. |
| FNIRSI USB Tester 4-28V 7A | `$52.99` | Keep if budget allows | Good for power telemetry baselines. Not mandatory for first SMS test, but valuable. |
| Gowoops SX1276 LoRa UART serial module | `$25.99` | Hold / remove | Not a first-node blocker. It is UART module hardware, while the current EVY validation defaults expect SPI/GPIO LoRa, and the Meshtastic spike should use supported Meshtastic node hardware instead. |
| SIM7600G-H 4G HAT | `$98.87` | Keep with band check | Correct class of modem. Waveshare direct pricing was lower at review time, but Amazon speed may be worth it. Verify antennas and SIM accessories are included. |
| GeeekPi P33 M.2 NVMe M-Key PoE+ HAT with cooler | `$37.99` | Hold / remove for first bring-up | It adds mechanical, power, PCIe, and HAT-stacking variables. It may conflict with the LTE HAT. Use microSD first; add NVMe/PoE after GSM + BitNet are stable. |
| RasTech Pi 5 GaN PD 27W power supply | `$12.99` | Swap | Use the official Raspberry Pi 27W USB-C PSU for first bring-up. |
| Raspberry Pi 5 16GB from MemoryWhiz | `$338.94` | Buy only if schedule beats cost | Raspberry Pi's official page listed Pi 5 16GB at `$305` during this review, so the cart price is a premium. Prefer an Approved Reseller. For first EVY, 8GB is acceptable; 16GB is nice but not required. |

## Missing From The Cart

- 2x high-endurance microSD cards, 128GB or larger.
- SMS-capable SIM card and plan.
- LTE antennas and GNSS antenna if the SIM7600 package does not include them.
- Ethernet cable if not already on hand.
- Pi 5-compatible case or bench standoffs that fit with the LTE HAT.
- Optional RTC battery for timestamp accuracy during offline testing.
- Optional USB SSD only after the microSD path is proven.

## Hold Until After GSM And BitNet Are Stable

- LoRa/Meshtastic hardware.
- PoE and NVMe HATs.
- Solar panel, charge controller, battery, and weatherproof enclosure.
- External watchdog/power-control board.
- Multi-node mesh accessories.

For the Meshtastic spike, prefer a complete Meshtastic-supported 915 MHz node such as a RAK WisBlock starter kit, Heltec T114-class node, LilyGO T-Beam-class node, or another currently supported device. For a direct Pi LoRa path, buy a Raspberry Pi LoRa HAT that exposes SPI and GPIO in a way that matches the EVY validation defaults.

## First Bench Assembly

Use the smallest reliable stack:

1. Raspberry Pi 5.
2. Official 27W USB-C power supply.
3. Official active cooler.
4. High-endurance microSD.
5. SIM7600-class LTE/GSM HAT.
6. Micro HDMI, Ethernet, keyboard, and UART adapter available for recovery.
7. USB power meter inline only when measuring power, not while debugging power instability.

Avoid stacking the PoE/NVMe HAT and LTE HAT for the first test. Prove one outbound SMS, one inbound SMS, and one integrated SMS to BitNet/RAG response before adding more hardware.

## Source Notes

- Raspberry Pi 5 official product page: Pi 5 supports USB 3, Gigabit Ethernet, PCIe via separate adapter, PoE+ via separate HAT, 5V/5A USB-C Power Delivery, 40-pin header, and active cooling is recommended for best performance.
- Raspberry Pi 27W USB-C power supply page: official supply is specified for 5.1V/5A output and is described as ideal for Raspberry Pi 5, especially with higher-power peripherals.
- Raspberry Pi Active Cooler page: official clip-on cooler is designed for Raspberry Pi 5 sustained thermal control.
- Waveshare SIM7600G-H product page: SIM7600G-H supports LTE/3G/2G, SMS, GNSS, Raspberry Pi 40-pin header, USB/UART AT-command access, and region-specific variants.
- Raspberry Pi Approved Reseller page: approved resellers are Raspberry Pi's trusted purchasing channel.
- Meshtastic project docs: Meshtastic is the right later path for off-grid LoRa mesh evaluation, but it is not a blocker for the first GSM/BitNet bench node.
