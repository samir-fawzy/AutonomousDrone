from __future__ import annotations
from pathlib import Path
from typing import Any
import numpy as np
import cv2  # مهمة جداً للتعامل مع الصور
from datetime import datetime
import os

class VisionService:
    """مسؤول عن سحب الصور من AirSim، اكتشاف الأجسام بـ YOLO، وحفظ النتائج."""

    def __init__(self, project_root: Path, logger):
        self.logger = logger
        self.project_root = project_root
        self.weights_path = project_root / "models" / "best.pt"
        self.model = self._load_model()
        
        # التأكد من وجود مجلد حفظ الصور عند بدء التشغيل
        self.save_dir = project_root / "data" / "raw_images"
        self.save_dir.mkdir(parents=True, exist_ok=True)

    def _load_model(self):
        """تحميل موديل YOLO من الهارد ديسك."""
        try:
            from ultralytics import YOLO
            if self.weights_path.exists():
                self.logger.info("Loading YOLO model from %s", self.weights_path)
                return YOLO(str(self.weights_path))
            self.logger.warning("YOLO weights not found at %s", self.weights_path)
        except Exception as exc:
            self.logger.warning("Could not initialize YOLO model: %s", exc)
        return None

    def get_frame(self, client) -> np.ndarray:
        """سحب الصورة الحقيقية من محاكي AirSim."""
        import airsim
        # طلب صورة "Scene" (ملونة) من الكاميرا الأمامية "0"
        responses = client.simGetImages([
            airsim.ImageRequest("0", airsim.ImageType.Scene, False, False)
        ])
        response = responses[0]
        
        # تحويل البيانات الخام (Bytes) إلى مصفوفة أرقام (NumPy)
        img1d = np.frombuffer(response.image_data_uint8, dtype=np.uint8)
        
        # إعادة تشكيل المصفوفة لتصبح صورة (Height, Width, Channels)
        # ملاحظة: OpenCV بيتعامل مع الصور كـ BGR
        frame = img1d.reshape(response.height, response.width, 3)
        return frame

    def detect_objects(self, frame: np.ndarray) -> list[dict[str, Any]]:
        """تحليل الصورة وإرجاع قائمة بالأجسام المكتشفة."""
        if self.model is None:
            return []

        results = self.model(frame, verbose=False)
        detections = []

        for result in results:
            names = result.names
            for box in result.boxes:
                cls_id = int(box.cls.item())
                conf = float(box.conf.item())
                # إحداثيات المربع [x_start, y_start, x_end, y_end]
                coords = box.xyxy[0].tolist()
                
                detections.append({
                    "label": names.get(cls_id, str(cls_id)),
                    "confidence": conf,
                    "bbox": coords,
                })
        return detections

    def save_detected_frame(self, frame: np.ndarray, detections: list[dict[str, Any]]):
        """حفظ الصورة فقط إذا تم اكتشاف أجسام، مع رسم المربعات عليها."""
        if len(detections) > 0:
            # صنع نسخة من الصورة عشان مانرسمش على الصورة الأصلية اللي رايحة للـ Planner
            debug_frame = frame.copy()
            
            # رسم المربعات والأسماء
            for obj in detections:
                x1, y1, x2, y2 = map(int, obj["bbox"])
                label = f"{obj['label']} {obj['confidence']:.2f}"
                
                # رسم المستطيل (لون أخضر، سمك 2)
                cv2.rectangle(debug_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                # كتابة اسم الجسم فوق المربع
                cv2.putText(debug_frame, label, (x1, y1 - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # تجهيز المسار والاسم
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            file_path = self.save_dir / f"detected_{timestamp}.jpg"
            
            # حفظ الصورة
            cv2.imwrite(str(file_path), debug_frame)
            self.logger.debug(f"Saved detection: {file_path}")