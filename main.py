from __future__ import annotations

import time
from pathlib import Path

from controllers.drone_controller import DroneController
from intelligence.path_planner import PathPlanner
from intelligence.rl_agent import RLAgent
from services.vision_service import VisionService
from utils.logger import setup_logger

import math
def run_control_loop() -> None:
    """Main Sense-Think-Act loop for the autonomous drone."""
    project_root = Path(__file__).resolve().parent
    logger = setup_logger(log_dir=project_root / "data" / "logs")
    logger.info("Starting autonomous drone control loop.")

    vision = VisionService(project_root=project_root, logger=logger)
    controller = DroneController(logger=logger)
    planner = PathPlanner(logger=logger)
    agent = RLAgent(logger=logger)

    try:
        controller.connect()
        controller.takeoff()

        for step in range(100):
            frame = vision.get_frame(controller.client)  # الصورة بتيجي مصفوفة مباشرة
            detections = vision.detect_objects(frame)

            state = {
                "step": step,
                "drone_pose": controller.get_pose(),
                "detections": detections,
            }
            action = agent.select_action(state)
            movement_cmd = planner.plan_next_move(detections=detections, rl_action=action)
            
            controller.move(**movement_cmd)

            logger.info("Step %s completed. action=%s", step, action)
            time.sleep(0.1)

            frame = vision.get_frame(controller.client)
            detections = vision.detect_objects(frame)
            vision.save_detected_frame(frame, detections)

    except KeyboardInterrupt:
        logger.warning("Control loop interrupted by user.")
    except Exception as exc:
        logger.exception("Unexpected error in control loop: %s", exc)

    # try:
    #     controller.connect()
    #     controller.takeoff()
        
    #     start_pose = controller.get_pose()
    #     target_distance = 100.0  # الـ 100 متر اللي إنت عايزهم
    #     reached_target = False

    #     while not reached_target:
    #         current_pose = controller.get_pose()
    #         distance_covered = calculate_distance(start_pose, current_pose)
            
    #         # 1. Sense
    #         frame = vision.get_frame(controller.client)
    #         detections = vision.detect_objects(frame)

    #         # 2. Think (RL Agent)
    #         # الـ RL هنا وظيفته الأساسية هي الـ Obstacle Avoidance 
    #         # عشان وهو ماشي الـ 100 متر ميتخبطش في حاجة
    #         state = {"pose": current_pose, "detections": detections}
    #         action = agent.select_action(state)
            
    #         # 3. Act
    #         if distance_covered < target_distance:
    #             # بنقول للدرون كملي لقدام بس خلي بالك من العوائق
    #             movement_cmd = planner.plan_next_move(detections=detections, rl_action=action)
    #             controller.move(**movement_cmd)
                
    #             print(f"Distance covered: {distance_covered:.2f} / 100m", end="\r")
    #         else:
    #             logger.info("Goal Reached! 100 meters covered.")
    #             reached_target = True

    #         time.sleep(0.05) # تقليل الـ delay عشان الدقة تزيد

    except KeyboardInterrupt:
        logger.warning("Interrupted!")
    finally:
        controller.land()
        controller.disconnect()
        logger.info("Control loop terminated safely.")


def calculate_distance(p1, p2):
    # p1, p2 are dicts like {'x': 0, 'y': 0, 'z': 0}
    return math.sqrt((p1['x'] - p2['x'])**2 + (p1['y'] - p2['y'])**2)

if __name__ == "__main__":
    run_control_loop()
