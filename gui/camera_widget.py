from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QComboBox, QMessageBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QImage
import cv2


class CameraWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.camera = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # 摄像头选择区域
        camera_control_layout = QHBoxLayout()
        
        self.camera_combo = QComboBox()
        self.refresh_cameras()
        
        self.btn_refresh = QPushButton("刷新摄像头")
        self.btn_refresh.clicked.connect(self.refresh_cameras)
        
        self.btn_start = QPushButton("开始检测")
        self.btn_start.clicked.connect(self.start_camera)
        
        self.btn_stop = QPushButton("停止检测")
        self.btn_stop.clicked.connect(self.stop_camera)
        self.btn_stop.setEnabled(False)
        
        camera_control_layout.addWidget(QLabel("选择摄像头:"))
        camera_control_layout.addWidget(self.camera_combo)
        camera_control_layout.addWidget(self.btn_refresh)
        camera_control_layout.addWidget(self.btn_start)
        camera_control_layout.addWidget(self.btn_stop)
        camera_control_layout.addStretch()
        
        # 摄像头显示区域
        self.camera_label = QLabel("摄像头未启动")
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setStyleSheet("border: 1px solid black; background-color: #f0f0f0;")
        self.camera_label.setMinimumSize(640, 480)
        
        # 状态标签
        self.status_label = QLabel("状态: 未连接")
        self.status_label.setAlignment(Qt.AlignCenter)
        
        layout.addLayout(camera_control_layout)
        layout.addWidget(self.camera_label)
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)

    def refresh_cameras(self):
        """刷新可用摄像头列表"""
        self.camera_combo.clear()
        self.camera_combo.addItem("请选择摄像头", -1)
        
        # 检测可用的摄像头
        for i in range(10):  # 检查前10个摄像头索引
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                self.camera_combo.addItem(f"摄像头 {i}", i)
                cap.release()

    def start_camera(self):
        """启动摄像头"""
        if self.camera_combo.currentData() == -1:
            QMessageBox.warning(self, "警告", "请先选择一个摄像头")
            return
        
        camera_index = self.camera_combo.currentData()
        self.camera = cv2.VideoCapture(camera_index)
        
        if not self.camera.isOpened():
            QMessageBox.critical(self, "错误", f"无法打开摄像头 {camera_index}")
            return
        
        # 设置摄像头参数
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.camera.set(cv2.CAP_PROP_FPS, 30)
        
        # 启动定时器
        self.timer.start(33)  # 约30FPS
        
        # 更新UI状态
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.camera_combo.setEnabled(False)
        self.status_label.setText("状态: 运行中")

    def stop_camera(self):
        """停止摄像头"""
        if self.camera:
            self.timer.stop()
            self.camera.release()
            self.camera = None
        
        # 更新UI状态
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.camera_combo.setEnabled(True)
        self.camera_label.setText("摄像头未启动")
        self.status_label.setText("状态: 已停止")

    def update_frame(self):
        """更新摄像头帧"""
        if not self.camera or not self.camera.isOpened():
            return
        
        ret, frame = self.camera.read()
        if ret:
            # 转换图像格式用于显示
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            
            # 缩放图像以适应显示区域
            pixmap = QPixmap.fromImage(qt_image)
            scaled_pixmap = pixmap.scaled(self.camera_label.size(), 
                                        Qt.KeepAspectRatio, 
                                        Qt.SmoothTransformation)
            self.camera_label.setPixmap(scaled_pixmap)

    def get_current_frame(self):
        """获取当前帧用于检测"""
        if self.camera and self.camera.isOpened():
            ret, frame = self.camera.read()
            if ret:
                return frame
        return None

    def closeEvent(self, event):
        """关闭事件"""
        self.stop_camera()
        event.accept() 