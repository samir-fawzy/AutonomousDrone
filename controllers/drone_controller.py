from __future__ import annotations

from typing import Any


class DroneController:
    """Abstraction layer for controlling AirSim drone commands."""

    def __init__(self, logger):
        self.logger = logger
        self.client = None
        self.connected = False

    def connect(self) -> None:
        try:
            import airsim  # type: ignore

            self.client = airsim.MultirotorClient()
            self.client.confirmConnection()
            self.client.enableApiControl(True)
            self.client.armDisarm(True)
            self.connected = True
            self.logger.info("Connected to AirSim.")
        except Exception as exc:
            self.logger.warning("AirSim connection unavailable. Running in dry mode: %s", exc)

    def disconnect(self) -> None:
        if self.client is not None and self.connected:
            self.client.armDisarm(False)
            self.client.enableApiControl(False)
        self.logger.info("Drone disconnected.")

    def takeoff(self) -> None:
        if self.client is not None and self.connected:
            self.client.takeoffAsync().join()
        self.logger.info("Takeoff command sent.")

    def land(self) -> None:
        if self.client is not None and self.connected:
            self.client.landAsync().join()
        self.logger.info("Land command sent.")

    def move(self, vx: float, vy: float, vz: float, duration: float) -> None:
        if self.client is not None and self.connected:
            self.client.moveByVelocityAsync(vx, vy, vz, duration).join()
        self.logger.debug("Move command: vx=%.2f vy=%.2f vz=%.2f d=%.2f", vx, vy, vz, duration)

    def get_pose(self) -> dict[str, Any]:
        if self.client is not None and self.connected:
            state = self.client.getMultirotorState()
            return {
                "x": state.kinematics_estimated.position.x_val,
                "y": state.kinematics_estimated.position.y_val,
                "z": state.kinematics_estimated.position.z_val,
            }
        return {"x": 0.0, "y": 0.0, "z": 0.0}
