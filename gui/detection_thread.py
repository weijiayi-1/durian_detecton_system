import os
import cv2
from PyQt5.QtCore import QThread, pyqtSignal
from durian_detection_system.models.durian_detector import DurianDetector
from durian_detection_system.models.database import DatabaseManager


class DetectionThread(QThread):
    update_signal = pyqtSignal(dict)
    finished_signal = pyqtSignal()
    progress_signal = pyqtSignal(int)

    def __init__(self, detector, db_manager, source, is_video=False, is_camera=False, 
                 confidence_threshold=0.5, iou_threshold=0.45):
        super().__init__()
        self.detector = detector
        self.db_manager = db_manager
        self.source = source
        self.is_video = is_video
        self.is_camera = is_camera
        self.confidence_threshold = confidence_threshold
        self.iou_threshold = iou_threshold
        self.running = True

    def run(self):
        if self.is_camera:
            self.process_camera()
        elif os.path.isdir(self.source):
            self.process_folder()
        elif self.is_video:
            self.process_video()
        else:
            self.process_single_image(self.source)

    def process_single_image(self, image_path):
        detections = self.detector.detect(image_path, 
                                        conf=self.confidence_threshold, 
                                        iou=self.iou_threshold)
        if detections:
            for detection in detections:
                self.db_manager.save_detection(image_path, detection)
                self.update_signal.emit({
                    'type': 'image',
                    'path': image_path,
                    'detection': detection
                })
        self.finished_signal.emit()

    def process_folder(self):
        image_files = [f for f in os.listdir(self.source)
                       if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        total = len(image_files)

        for i, filename in enumerate(image_files):
            if not self.running:
                break

            image_path = os.path.join(self.source, filename)
            self.process_single_image(image_path)
            self.progress_signal.emit(int((i + 1) / total * 100))

        self.finished_signal.emit()

    def process_video(self):
        cap = cv2.VideoCapture(self.source)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_count = 0

        while self.running and cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            if frame_count % 10 != 0:  # 每10帧处理一次
                continue

            # 临时保存帧为图像进行处理
            temp_path = "temp_frame.jpg"
            cv2.imwrite(temp_path, frame)

            detections = self.detector.detect(temp_path, 
                                            conf=self.confidence_threshold, 
                                            iou=self.iou_threshold)
            if detections:
                for detection in detections:
                    self.db_manager.save_detection(temp_path, detection)
                    self.update_signal.emit({
                        'type': 'video_frame',
                        'frame': frame,
                        'detection': detection
                    })

            self.progress_signal.emit(int(frame_count / total_frames * 100))

        cap.release()
        if os.path.exists(temp_path):
            os.remove(temp_path)
        self.finished_signal.emit()

    def process_camera(self):
        cap = cv2.VideoCapture(self.source)
        
        while self.running and cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # 临时保存帧为图像进行处理
            temp_path = "temp_camera_frame.jpg"
            cv2.imwrite(temp_path, frame)

            detections = self.detector.detect(temp_path, 
                                            conf=self.confidence_threshold, 
                                            iou=self.iou_threshold)
            if detections:
                for detection in detections:
                    self.db_manager.save_detection(temp_path, detection)
                    self.update_signal.emit({
                        'type': 'camera_frame',
                        'frame': frame,
                        'detection': detection
                    })
            else:
                # 即使没有检测到也要发送帧用于显示
                self.update_signal.emit({
                    'type': 'camera_frame',
                    'frame': frame,
                    'detection': None
                })

        cap.release()
        if os.path.exists(temp_path):
            os.remove(temp_path)
        self.finished_signal.emit()

    def stop(self):
        self.running = False 