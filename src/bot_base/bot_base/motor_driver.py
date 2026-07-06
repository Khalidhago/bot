"""Motor driver interface for the bot base.

Two implementations are provided:

* MockMotorDriver — a perfect first-order simulation of the drivetrain, used
  for development, demos and CI with no hardware attached.
* SerialMotorDriver — speaks a simple ASCII line protocol to a motor
  controller (e.g. an Arduino/ESP32 running the matching firmware):

      host  -> mcu:   "v <left_rad_s> <right_rad_s>\n"   set wheel setpoints
      mcu   -> host:  "f <left_rad_s> <right_rad_s>\n"   measured wheel speeds,
                                                          streamed continuously

  Any malformed feedback lines are ignored; the last good measurement is
  retained.
"""
import threading
from abc import ABC, abstractmethod


class MotorDriver(ABC):
    """Abstract interface between the base controller and the motor hardware."""

    @abstractmethod
    def set_wheel_speeds(self, left: float, right: float) -> None:
        """Command wheel angular speeds in rad/s."""

    @abstractmethod
    def get_wheel_speeds(self) -> tuple[float, float]:
        """Return the latest measured (left, right) wheel speeds in rad/s."""

    def stop(self) -> None:
        self.set_wheel_speeds(0.0, 0.0)

    def close(self) -> None:
        """Release hardware resources. Safe to call more than once."""


class MockMotorDriver(MotorDriver):
    """Simulated drivetrain: measured speed tracks the setpoint through a
    first-order low-pass, which is a reasonable stand-in for a real motor's
    response and keeps odometry realistic in demos."""

    def __init__(self, time_constant: float = 0.15):
        self._time_constant = max(1e-3, time_constant)
        self._setpoint = (0.0, 0.0)
        self._measured = [0.0, 0.0]
        self._lock = threading.Lock()

    def set_wheel_speeds(self, left: float, right: float) -> None:
        with self._lock:
            self._setpoint = (left, right)

    def get_wheel_speeds(self) -> tuple[float, float]:
        with self._lock:
            return tuple(self._measured)

    def advance(self, dt: float) -> None:
        """Step the simulation by *dt* seconds. Called by the base node's
        control loop; a real driver receives feedback asynchronously instead."""
        alpha = min(1.0, dt / self._time_constant)
        with self._lock:
            for i in range(2):
                self._measured[i] += alpha * (self._setpoint[i] - self._measured[i])


class SerialMotorDriver(MotorDriver):
    """Driver for a serial-attached motor controller (see module docstring
    for the wire protocol)."""

    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 0.1):
        import serial  # local import: python3-serial is not needed for mock runs
        self._serial = serial.Serial(port, baudrate=baudrate, timeout=timeout)
        self._measured = (0.0, 0.0)
        self._lock = threading.Lock()
        self._running = True
        self._reader = threading.Thread(target=self._read_loop, daemon=True)
        self._reader.start()

    def set_wheel_speeds(self, left: float, right: float) -> None:
        self._serial.write(f'v {left:.4f} {right:.4f}\n'.encode('ascii'))

    def get_wheel_speeds(self) -> tuple[float, float]:
        with self._lock:
            return self._measured

    def close(self) -> None:
        self._running = False
        if self._serial.is_open:
            self.stop()
            self._serial.close()

    def _read_loop(self) -> None:
        while self._running:
            try:
                line = self._serial.readline().decode('ascii', errors='ignore').strip()
            except Exception:
                break  # port closed or unplugged; keep last measurement
            parts = line.split()
            if len(parts) == 3 and parts[0] == 'f':
                try:
                    left, right = float(parts[1]), float(parts[2])
                except ValueError:
                    continue
                with self._lock:
                    self._measured = (left, right)
