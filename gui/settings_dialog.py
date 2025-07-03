from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QSlider, QPushButton, QSpinBox, QDoubleSpinBox,
                             QGroupBox, QFormLayout)
from PyQt5.QtCore import Qt


class SettingsDialog(QDialog):
    def __init__(self, parent=None, confidence=0.5, iou=0.45):
        super().__init__(parent)
        self.confidence = confidence
        self.iou = iou
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("检测设置")
        self.setFixedSize(400, 300)
        
        layout = QVBoxLayout()
        
        # 置信度设置组
        confidence_group = QGroupBox("置信度阈值")
        confidence_layout = QFormLayout()
        
        self.confidence_slider = QSlider(Qt.Horizontal)
        self.confidence_slider.setRange(1, 100)
        self.confidence_slider.setValue(int(self.confidence * 100))
        self.confidence_slider.valueChanged.connect(self.on_confidence_slider_changed)
        
        self.confidence_spinbox = QDoubleSpinBox()
        self.confidence_spinbox.setRange(0.01, 1.0)
        self.confidence_spinbox.setSingleStep(0.01)
        self.confidence_spinbox.setValue(self.confidence)
        self.confidence_spinbox.valueChanged.connect(self.on_confidence_spinbox_changed)
        
        confidence_layout.addRow("置信度:", self.confidence_spinbox)
        confidence_layout.addRow("", self.confidence_slider)
        confidence_group.setLayout(confidence_layout)
        
        # IOU设置组
        iou_group = QGroupBox("IOU阈值")
        iou_layout = QFormLayout()
        
        self.iou_slider = QSlider(Qt.Horizontal)
        self.iou_slider.setRange(1, 100)
        self.iou_slider.setValue(int(self.iou * 100))
        self.iou_slider.valueChanged.connect(self.on_iou_slider_changed)
        
        self.iou_spinbox = QDoubleSpinBox()
        self.iou_spinbox.setRange(0.01, 1.0)
        self.iou_spinbox.setSingleStep(0.01)
        self.iou_spinbox.setValue(self.iou)
        self.iou_spinbox.valueChanged.connect(self.on_iou_spinbox_changed)
        
        iou_layout.addRow("IOU:", self.iou_spinbox)
        iou_layout.addRow("", self.iou_slider)
        iou_group.setLayout(iou_layout)
        
        # 说明文本
        info_label = QLabel("置信度阈值：控制检测结果的可靠性，值越高检测越严格\n"
                           "IOU阈值：控制重叠检测框的合并，值越高合并越严格")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: gray; font-size: 10px;")
        
        # 按钮
        button_layout = QHBoxLayout()
        self.btn_ok = QPushButton("确定")
        self.btn_cancel = QPushButton("取消")
        self.btn_reset = QPushButton("重置默认")
        
        self.btn_ok.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_reset.clicked.connect(self.reset_to_default)
        
        button_layout.addWidget(self.btn_reset)
        button_layout.addStretch()
        button_layout.addWidget(self.btn_cancel)
        button_layout.addWidget(self.btn_ok)
        
        # 添加到主布局
        layout.addWidget(confidence_group)
        layout.addWidget(iou_group)
        layout.addWidget(info_label)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)

    def on_confidence_slider_changed(self, value):
        self.confidence = value / 100.0
        self.confidence_spinbox.setValue(self.confidence)

    def on_confidence_spinbox_changed(self, value):
        self.confidence = value
        self.confidence_slider.setValue(int(value * 100))

    def on_iou_slider_changed(self, value):
        self.iou = value / 100.0
        self.iou_spinbox.setValue(self.iou)

    def on_iou_spinbox_changed(self, value):
        self.iou = value
        self.iou_slider.setValue(int(value * 100))

    def reset_to_default(self):
        self.confidence = 0.5
        self.iou = 0.45
        self.confidence_slider.setValue(50)
        self.iou_slider.setValue(45)
        self.confidence_spinbox.setValue(0.5)
        self.iou_spinbox.setValue(0.45)

    def get_settings(self):
        return {
            'confidence': self.confidence,
            'iou': self.iou
        } 