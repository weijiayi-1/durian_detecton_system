from ultralytics import YOLO
import cv2
import numpy as np
from durian_detection_system.config.settings import config


class DurianDetector:
    def __init__(self):
        # 加载两个模型
        self.sort_model = YOLO(config.SORT_MODEL_PATH)
        self.maturity_model = YOLO(config.MATURITY_MODEL_PATH)

    def detect(self, image_path, conf=0.5, iou=0.45):
        """
        检测榴莲种类和成熟度
        :param image_path: 图片路径或numpy数组
        :param conf: 置信度阈值
        :param iou: IOU阈值
        :return: 检测结果列表，每个元素是一个字典
        """
        # 如果传入的是路径则读取图像，否则直接使用numpy数组
        if isinstance(image_path, str):
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"无法读取图像: {image_path}")
        else:
            image = image_path

        # 检测种类
        sort_results = self.sort_model(image, conf=conf, iou=iou)[0]
        # 检测成熟度
        maturity_results = self.maturity_model(image, conf=conf, iou=iou)[0]

        detections = []

        # 处理种类检测结果
        for box in sort_results.boxes:
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])
            bbox = box.xyxy[0].tolist()

            if confidence < conf:  # 使用传入的置信度阈值
                continue

            detection = {
                'bbox': bbox,
                'sort': config.SORT_CLASSES[class_id],
                'sort_confidence': confidence,
                'maturity': 'unknown',  # 默认值
                'maturity_confidence': 0.0,  # 默认值
                'status': 'unknown'  # 默认值
            }

            # 获取对应的成熟度检测结果
            maturity_info = self._get_maturity_for_bbox(bbox, maturity_results, conf, iou)
            if maturity_info:
                detection['maturity'] = maturity_info['class_name']
                detection['maturity_confidence'] = maturity_info['confidence']
                detection['status'] = config.MATURITY_STATUS.get(maturity_info['class_name'], '未知')

            detections.append(detection)

        return detections

    # ... 其余方法保持不变 ...
    def _get_maturity_for_bbox(self, bbox, maturity_results, conf=0.5, iou=0.45):
        """
        根据bbox获取对应的成熟度检测结果
        """
        x1, y1, x2, y2 = bbox
        bbox_center = [(x1 + x2) / 2, (y1 + y2) / 2]
        bbox_area = (x2 - x1) * (y2 - y1)

        best_match = None
        best_iou = 0

        for box in maturity_results.boxes:
            m_class_id = int(box.cls[0])
            m_confidence = float(box.conf[0])
            m_bbox = box.xyxy[0].tolist()

            if m_confidence < conf:  # 使用传入的置信度阈值
                continue

            # 计算IOU
            iou_value = self._calculate_iou(bbox, m_bbox)

            if iou_value > best_iou:
                best_iou = iou_value
                best_match = {
                    'class_name': config.MATURITY_CLASSES[m_class_id],
                    'confidence': m_confidence
                }

        return best_match if best_iou > iou else None  # 使用传入的IOU阈值

    def _calculate_iou(self, box1, box2):
        """
        计算两个bbox的IOU
        """
        # 计算交集区域
        x_left = max(box1[0], box2[0])
        y_top = max(box1[1], box2[1])
        x_right = min(box1[2], box2[2])
        y_bottom = min(box1[3], box2[3])

        if x_right < x_left or y_bottom < y_top:
            return 0.0

        intersection_area = (x_right - x_left) * (y_bottom - y_top)

        # 计算并集区域
        box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
        box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])

        iou = intersection_area / float(box1_area + box2_area - intersection_area)
        return iou