# Hardware

Reference builds that this software stack is developed and tested against.
Each document covers the bill of materials, wiring, power budget, and the
checklists used before the vehicle moves.

| Vehicle | Document | Software entry point |
| --- | --- | --- |
| Quadcopter (X450 class) | [quadcopter.md](quadcopter.md) | `ros2 launch uav_telemetry telemetry.launch.py` |
| Ground rover (diff-drive) | [rover.md](rover.md) | `ros2 launch bot_bringup robot.launch.py` |

## Design principles

- **Companion-computer architecture.** Flight-critical control always stays
  on a dedicated controller (Pixhawk for air, a microcontroller for ground).
  The Linux computer running ROS is never in the safety loop: if it crashes,
  the vehicle can still be stopped or landed from the RC link.
- **Every subsystem must run without its hardware.** Mock drivers
  (`bot_base` mock motors, `uav_telemetry` mock link) mean integration,
  demos, and CI never need a bench setup.
- **One number, one place.** Physical constants (wheel geometry, speed
  limits) live in a single config file and everything else reads them.
