# Ground rover reference build (differential drive)

The indoor development platform for the ground stack: mapping, navigation,
and the phone-teleop bridge are all tuned on this vehicle.

## Bill of materials

| Subsystem | Part | Qty | Notes |
| --- | --- | --- | --- |
| Chassis | 2WD aluminium chassis + rear caster, ~30 x 22 cm | 1 | matches `bot_description` |
| Motors | 12 V DC gearmotor with quadrature encoder, ~178 rpm | 2 | encoder needed for odometry |
| Wheels | 90 mm rubber | 2 | radius 0.045 m in `base.yaml` |
| Motor driver | Dual H-bridge (e.g. TB6612/L298-class) | 1 | sized for stall current |
| Microcontroller | Arduino/ESP32-class | 1 | runs the wheel-speed loop |
| Computer | Raspberry Pi 4 (2 GB+) | 1 | runs this ROS 2 stack |
| Lidar | 2D 360° lidar (~8 m range) | 1 | publishes `/scan` |
| Battery | 3S 18650 pack or 12 V pack + 5 V/3 A BEC | 1 | separate rail for logic |

## Wiring overview

```
 12 V pack ──► H-bridge ──► motors (encoders ──► microcontroller)
      │            ▲
      │            │ PWM + direction
      │       microcontroller ◄──USB serial (115200)──► Raspberry Pi 4
      └──► 5 V BEC ──► Raspberry Pi 4 + lidar
```

## Serial protocol (microcontroller ↔ `bot_base`)

The firmware runs the fast PID loop on wheel speed; ROS sends setpoints and
receives measurements. Plain ASCII lines at 115200 baud:

```
Pi  -> MCU:   v <left_rad_s> <right_rad_s>\n     wheel speed setpoints
MCU -> Pi:    f <left_rad_s> <right_rad_s>\n     measured speeds, ~50 Hz
```

Firmware must zero the motors if no `v` line arrives for 500 ms — same
deadman contract the ROS side applies to `cmd_vel`.

## Bring-up order

1. Bench: wheels off the ground, `use_mock_hardware:=false`, verify
   `ros2 topic echo /odom` responds to `v` commands and direction signs match.
2. Calibrate `wheel_radius` / `wheel_separation` in
   `src/bot_base/config/base.yaml`: drive 2 m straight and one full spin,
   correct by the measured error.
3. Phone teleop (`http://<pi>:8080`) in an open area.
4. Map with `slam.launch.py`, then navigate with `nav.launch.py`.
