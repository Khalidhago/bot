FROM ros:humble-ros-base

SHELL ["/bin/bash", "-c"]

RUN apt-get update && apt-get install -y --no-install-recommends \
        python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /ws
COPY src src

RUN apt-get update \
    && rosdep update \
    && rosdep install --from-paths src --ignore-src -y \
    && rm -rf /var/lib/apt/lists/*

RUN source /opt/ros/humble/setup.bash \
    && colcon build --symlink-install

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# 8080: joystick web UI, 9090: rosbridge websocket
EXPOSE 8080 9090

ENTRYPOINT ["/entrypoint.sh"]
CMD ["ros2", "launch", "bot_bringup", "robot.launch.py", "use_mock_hardware:=true"]
