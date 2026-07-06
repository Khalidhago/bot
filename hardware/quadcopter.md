# Quadcopter reference build (X450 class)

A 450 mm development quadcopter: big enough to lift a companion computer,
small and cheap enough to crash during development without drama.

## Bill of materials

| Subsystem | Part | Qty | Notes |
| --- | --- | --- | --- |
| Frame | S500/F450-class X frame, 450 mm | 1 | integrated PDB preferred |
| Motors | 2212 920 KV brushless | 4 | 2 CW + 2 CCW prop threads |
| ESCs | 30 A BLHeli_S, DShot capable | 4 | or a 4-in-1 30 A |
| Props | 10x4.5 self-locking | 2 sets | always stock spares |
| Flight controller | Pixhawk 6C (PX4) | 1 | ArduPilot also supported |
| GPS | M10 GNSS + compass, on mast | 1 | keep away from power wiring |
| Companion computer | Raspberry Pi 4 (4 GB) | 1 | runs this ROS 2 stack |
| FC ↔ companion link | UART (TELEM2) at 921600 baud | — | MAVLink 2 |
| RC | ELRS/other 2.4 GHz receiver + transmitter | 1 | the manual override path |
| Telemetry (optional) | 915/433 MHz SiK radio pair | 1 | ground station link |
| Battery | 4S 5200 mAh LiPo, XT60 | 1+ | see power budget |
| Power module | Voltage/current sensor for FC | 1 | calibrate before first flight |
| Pi power | 5 V / 3 A BEC from main bus | 1 | never power the Pi from a Pixhawk rail |

## Power budget (hover, indicative)

| Load | Draw |
| --- | --- |
| 4 x motors at hover (~50% throttle) | ~14 A |
| Raspberry Pi 4 + peripherals | ~1.2 A at 5 V (≈0.5 A at 14.8 V) |
| FC, GPS, receiver, radio | ~0.5 A |
| **Total at hover** | **~15 A** |

4S 5200 mAh at 15 A ≈ 17 min theoretical; plan missions around **10–12 min**
with a 25% reserve, and set the failsafe battery action accordingly.

## Wiring overview

```
 4S LiPo ──► power module ──► PDB ──► 4x ESC ──► motors
                │                └──► 5V BEC ──► Raspberry Pi 4
                └──► Pixhawk 6C (POWER1)
                        │ TELEM2 (UART, MAVLink 2, 921600)
                        ▼
                  Raspberry Pi 4 ──► ROS 2 stack (uav_telemetry, rosbridge)
                        │
                        └──► Wi-Fi ──► phone / ground station dashboard
```

- Twist motor phase wires; keep GPS/compass on a mast above the power wiring.
- Common ground between PDB, FC, and Pi — one star point, no loops.
- Secure the battery with two straps; a shifting pack moves the CG mid-flight.

## Companion computer bring-up

```bash
# On the Pi, after building this repo:
ros2 launch uav_telemetry telemetry.launch.py connection_url:=/dev/ttyAMA0
ros2 topic echo /mavlink_bridge/battery
```

PX4 side: set `MAV_1_CONFIG = TELEM2`, `SER_TEL2_BAUD = 921600`.

## Preflight checklist

1. Props off for any bench test involving arming. No exceptions.
2. Frame bolts, motor mounts, prop nuts torqued; props correct rotation.
3. Battery charged, secured, voltage verified at the FC (calibrated sensor).
4. GPS 3D fix with ≥ 8 satellites; compass variance nominal.
5. RC failsafe verified: transmitter off ⇒ configured failsafe action.
6. Geofence and battery failsafe set for the site.
7. Telemetry visible in ground station and on the ROS topics.
8. Clear area, spotter briefed, flight mode and RTL altitude confirmed.

## Regulatory note

Operate under your local aviation rules (registration, remote ID, maximum
altitude, visual line of sight, no-fly zones). Rules differ by country and
change often — check before every new site.
