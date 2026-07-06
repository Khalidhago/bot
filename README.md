# bot — ROS 2 robotics stack, ground and air

A complete ROS 2 (Humble) stack for unmanned vehicles, built by
[Hago Drone Consulting Services](https://github.com/Khalidhago):
a differential-drive ground rover with SLAM/Nav2 autonomy and phone-based
teleoperation, plus a MAVLink telemetry bridge for PX4/ArduPilot aircraft.

Every subsystem ships with a mock hardware implementation, so the entire
stack runs on a laptop or in CI with nothing plugged in.

## Packages

| Package             | Domain | Purpose                                                        |
| ------------------- | ------ | -------------------------------------------------------------- |
| `bot_description`   | ground | URDF/xacro robot model, RViz display                           |
| `bot_base`          | ground | Diff-drive controller: `/cmd_vel` → wheels, odometry → `/odom` + TF |
| `bot_mobile_bridge` | shared | rosbridge websocket + touch-joystick web UI served to phones   |
| `bot_navigation`    | ground | SLAM Toolbox and Nav2 configuration and launch files           |
| `bot_bringup`       | ground | Top-level launch files composing the system                    |
| `uav_telemetry`     | air    | MAVLink → ROS 2 bridge: GPS, battery, attitude, mode, arming   |

Hardware reference builds (BOM, wiring, power budgets, checklists) are
documented in [`hardware/`](hardware/README.md).

## Architecture (ground)

```
 phone browser ──ws──► rosbridge ──► /cmd_vel_mobile ─┐  (priority 100)
 joystick / keyboard ─────────────► /cmd_vel_teleop ──┤  (priority 90)
                                                      ├─► twist mux ─► /cmd_vel_base ─► bot_base ─► motors
 Nav2 velocity smoother ──────────► /cmd_vel ─────────┘  (priority 10)          │
                                                                                └─► /odom, TF (odom→base_footprint)
 lidar ─► /scan ─► slam_toolbox / AMCL ─► TF (map→odom)
```

`bot_base` abstracts the motor hardware behind a small driver interface
(`MotorDriver`): a `MockMotorDriver` simulates the drivetrain for desk and
CI runs; a `SerialMotorDriver` speaks a line protocol to a microcontroller
(documented in [`hardware/rover.md`](hardware/rover.md)).

## Architecture (air)

```
 Pixhawk (PX4/ArduPilot) ──MAVLink/UART──► uav_telemetry ──► /mavlink_bridge/global_position (NavSatFix)
                                                        ├──► /mavlink_bridge/battery         (BatteryState)
                                                        ├──► /mavlink_bridge/attitude        (Imu)
                                                        └──► /mavlink_bridge/armed, /flight_mode
```

Flight-critical control stays on the flight controller; the companion
computer only consumes telemetry and is never in the safety loop.

## Quick start (no hardware)

```bash
# In a ROS 2 Humble environment:
rosdep install --from-paths src --ignore-src -y
colcon build --symlink-install
source install/setup.bash

# Ground stack with simulated drivetrain:
ros2 launch bot_bringup robot.launch.py use_mock_hardware:=true

# UAV telemetry with a simulated aircraft:
ros2 launch uav_telemetry telemetry.launch.py use_mock_link:=true
```

Then open `http://<host-ip>:8080` on your phone (same network) and drive
with the on-screen joystick.

### Docker

```bash
docker compose up --build
```

## Mapping and navigation

```bash
# Build a map while driving around (phone joystick works well):
ros2 launch bot_bringup slam.launch.py

# Save it:
ros2 run nav2_map_server map_saver_cli -f maps/home

# Navigate autonomously on the saved map:
ros2 launch bot_bringup nav.launch.py map:=maps/home.yaml
```

## Connecting a real aircraft

```bash
# Serial from a companion computer (PX4 TELEM2, MAVLink 2):
ros2 launch uav_telemetry telemetry.launch.py connection_url:=/dev/ttyAMA0

# Or UDP from SITL / a telemetry radio:
ros2 launch uav_telemetry telemetry.launch.py connection_url:=udp:0.0.0.0:14550
```

## Tests

```bash
colcon test && colcon test-result --verbose
```

Unit tests cover the drive kinematics and odometry math, the MAVLink unit
conversions, and the web UI's safety invariants. CI builds and tests every
package on `ros:humble` for each push.

## License

[MIT](LICENSE)
