# Sentinel S3 Box 3 — Voice Assistant + Sensor Dock (TezSolutions fork)

Sentinel-branded alternate firmware for the ESP32-S3-BOX-3 with the Sensor Dock,
forked from [AlmostInteractive/ESP32-S3-Box-3-Voice-Assistant-Sensor-Dock](https://github.com/AlmostInteractive/ESP32-S3-Box-3-Voice-Assistant-Sensor-Dock).

## What changed vs upstream (v1.3.2-sentinel.1)

- **Sentinel theme UI**: all VA state icons recolored to the TezSentinel palette
  (brand blue `#1C5FA8`, cyan `#38BDF8`, thinking purple `#A855F7`, error red
  `#EF4444`, idle steel `#6B7A8D`), UI accent colors retinted, and the boot
  splash rebranded to "Sentinel / S3 Box 3 / Loading ....." with an "S" monogram.
- **Self-contained assets**: fonts and images now load from this repo
  (`fonts/`, `images/`) instead of upstream raw URLs.
- **Touch-to-talk**: tapping the VA state picture on the Status page starts /
  stops the voice assistant (alongside all upstream touch controls — page nav
  arrows, IR slots, settings +/- buttons, red-circle mode toggle).

Everything else (IR learning/blasting, radar screensaver, battery/temp, HA
entities) is upstream behavior — see the upstream README for page-by-page
details, screenshots and the touchscreen-init-reboot note:
https://github.com/AlmostInteractive/ESP32-S3-Box-3-Voice-Assistant-Sensor-Dock

## Build

```bash
esphome compile esp32-s3-box-3.yaml
```

TODOs before flashing (search for "TODO" in `esp32-s3-box-3.yaml`):
`ota_password`, `encryption_key`, sound URLs, wake word model.

### Upstream resources

- https://github.com/BigBobbas/ESP32-S3-Box3-Custom-ESPHome
- https://github.com/esphome/firmware/tree/main/wake-word-voice-assistant
- https://github.com/AlmostInteractive/ESP32-S3-Box3-IR-Blaster-Learning-Example/
