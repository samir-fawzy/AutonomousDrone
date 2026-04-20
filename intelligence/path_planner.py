from __future__ import annotations

from typing import Any


class PathPlanner:
    """Converts perception + RL decisions into velocity commands."""

    def __init__(self, logger):
        self.logger = logger
        self.default_duration = 0.2

    def plan_next_move(self, detections: list[dict[str, Any]], rl_action: str) -> dict[str, float]:
        obstacle_ahead = self._is_obstacle_ahead(detections)

        if obstacle_ahead:
            self.logger.info("Obstacle detected ahead. Executing avoidance.")
            return {"vx": 0.0, "vy": 1.0, "vz": 0.0, "duration": self.default_duration}

        if rl_action == "forward":
            return {"vx": 2.0, "vy": 0.0, "vz": 0.0, "duration": self.default_duration}
        if rl_action == "left":
            return {"vx": 0.0, "vy": -1.0, "vz": 0.0, "duration": self.default_duration}
        if rl_action == "right":
            return {"vx": 0.0, "vy": 1.0, "vz": 0.0, "duration": self.default_duration}

        return {"vx": 0.0, "vy": 0.0, "vz": 0.0, "duration": self.default_duration}

    # def plan_next_move(self, detections: list[dict[str, Any]], rl_action: str) -> dict[str, float]:
    #     obstacle_ahead = self._is_obstacle_ahead(detections)

    #     # 1. حالة الطوارئ: لو فيه عائق، الأولوية للتفادي
    #     if obstacle_ahead:
    #         self.logger.warning("Obstacle detected! Executing avoidance based on RL.")
    #         # هنا نعتمد على الـ RL عشان يختار يتفادى يمين ولا شمال
    #         if rl_action == "left":
    #             return {"vx": 0.0, "vy": -2.0, "vz": 0.0, "duration": self.default_duration}
    #         elif rl_action == "right":
    #             return {"vx": 0.0, "vy": 2.0, "vz": 0.0, "duration": self.default_duration}
    #         else:
    #             # لو الـ RL مخرف وقال قدام بالرغم من وجود عائق، نفرض تفادي إجباري
    #             return {"vx": 0.0, "vy": 2.0, "vz": 0.0, "duration": self.default_duration}

    #     # 2. السلوك الافتراضي (Cruising): طالما الطريق أمان، انطلق للأمام
    #     # تجاهلنا الـ RL action هنا لو كان left/right طالما مفيش عائق عشان نمنع الرعشة
    #     self.logger.info("Path clear. Cruising forward.")
    #     return {"vx": 3.0, "vy": 0.0, "vz": 0.0, "duration": self.default_duration} # السرعة 3 لقطع مسافة أسرع

    # def _is_obstacle_ahead(self, detections: list[dict[str, Any]]) -> bool:
    #     for obj in detections:
    #         x1, _, x2, _ = obj.get("bbox", [0.0, 0.0, 0.0, 0.0])
    #         width = max(x2 - x1, 0.0)
    #         if width > 160:
    #             return True
    #     return False
