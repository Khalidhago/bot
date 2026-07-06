# bot — ROS 2 mobile robot stack

A complete ROS 2 (Humble) software stack for a differential-drive mobile robot,
including phone-based teleoperation: connect a mobile phone to the robot's
network and drive it from the browser — no app install required.

## Packages

| Package             | Type         | Purpose                                                        |
| ------------------- | ------------ | -------------------------------------------------------------- |
| `bot_description`   | ament_cmake  | URDF/xacro robot model, `robot_state_publisher`, RViz display  |
| `bot_base`          | ament_python | Differential-drive base controller: `/cmd_vel` → wheels, odometry → `/odom` + TF |
| `bot_mobile_bridge` | ament_python | rosbridge websocket + touch-joystick web UI served to phones   |
| `bot_navigation`    | ament_cmake  | SLAM Toolbox and Nav2 configuration and launch files           |
| `bot_bringup`       | ament_cmake  | Top-level launch files composing the system                    |

## Architecture

```
 phone browser ──ws──► rosbridge ──► /cmd_vel_mobile ─┐  (priority 100)
 joystick / keyboard ─────────────► /cmd_vel_teleop ──┤  (priority 90)
                                                      ├─► twist mux ─► /cmd_vel_base ─► bot_base ─► motors
 Nav2 velocity smoother ──────────► /cmd_vel ─────────┘  (priority 10)          │
                                                                                └─► /odom, TF (odom→base_footprint)
 lidar ─► /scan ─► slam_toolbox / AMCL ─► TF (map→odom)
```

`bot_base` abstracts the motor hardware behind a small driver interface
(`MotorDriver`). A `MockMotorDriver` is provided so the full stack runs
end-to-end on a laptop or in CI with no hardware attached; a
`SerialMotorDriver` speaks a simple line protocol to a microcontroller.

## Quick start (no hardware)

```bash
# In a ROS 2 Humble environment:
cd bot
rosdep install --from-paths src --ignore-src -y
colcon build --symlink-install
source install/setup.bash

ros2 launch bot_bringup robot.launch.py use_mock_hardware:=true
```

Then open `http://<robot-ip>:8080` on your phone (same network) and drive
with the on-screen joystick.

### Docker

```bash
docker compose up --build
```

## Mapping and navigation

```bash
# Build a map while driving around:
ros2 launch bot_bringup slam.launch.py

# Save it:
ros2 run nav2_map_server map_saver_cli -f maps/home

# Navigate autonomously on the saved map:
ros2 launch bot_bringup nav.launch.py map:=maps/home.yaml
```

## Tests

```bash
colcon test --packages-select bot_base bot_mobile_bridge
colcon test-result --verbose
```

## Hardware bring-up

Set `use_mock_hardware:=false` and configure the serial port in
`src/bot_base/config/base.yaml`. The expected microcontroller protocol is
documented in `src/bot_base/bot_base/motor_driver.py`.
