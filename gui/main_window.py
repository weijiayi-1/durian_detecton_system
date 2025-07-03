import os
from PyQt5.QtWidgets import (QMainWindow, QApplication, QFileDialog, QLabel,
                             QPushButton, QVBoxLayout, QWidget, QComboBox,
                             QHBoxLayout, QMessageBox, QProgressBar, QTabWidget,
                             QSplitter, QGroupBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
from durian_detection_system.models.durian_detector import DurianDetector
from durian_detection_system.models.database import DatabaseManager
from durian_detection_system.config.settings import config
from durian_detection_system.gui.detection_thread import DetectionThread
from durian_detection_system.gui.settings_dialog import SettingsDialog
from durian_detection_system.gui.camera_widget import CameraWidget
import cv2


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("榴莲种类和成熟度检测系统")
        self.setGeometry(100, 100, 1200, 800)

        # 初始化模型和数据库
        self.detector = DurianDetector()
        self.db_manager = DatabaseManager()
        self.detection_thread = None
        
        # 检测设置
        self.confidence_threshold = 0.5
        self.iou_threshold = 0.45

        # 主界面组件
        self.init_ui()

    def init_ui(self):
        # 主布局
        main_widget = QWidget()
        main_layout = QVBoxLayout()

        # 顶部工具栏
        toolbar_layout = QHBoxLayout()
        
        # 设置按钮
        self.btn_settings = QPushButton("检测设置")
        self.btn_settings.clicked.connect(self.open_settings)
        
        # 文件操作按钮
        self.btn_select_image = QPushButton("选择图片")
        self.btn_select_image.clicked.connect(self.select_image)

        self.btn_select_folder = QPushButton("选择文件夹")
        self.btn_select_folder.clicked.connect(self.select_folder)

        self.btn_select_video = QPushButton("选择视频")
        self.btn_select_video.clicked.connect(self.select_video)

        self.btn_stop = QPushButton("停止检测")
        self.btn_stop.clicked.connect(self.stop_detection)
        self.btn_stop.setEnabled(False)

        toolbar_layout.addWidget(self.btn_settings)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.btn_select_image)
        toolbar_layout.addWidget(self.btn_select_folder)
        toolbar_layout.addWidget(self.btn_select_video)
        toolbar_layout.addWidget(self.btn_stop)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setAlignment(Qt.AlignCenter)

        # 创建标签页
        self.tab_widget = QTabWidget()
        
        # 文件检测标签页
        self.file_tab = self.create_file_tab()
        self.tab_widget.addTab(self.file_tab, "文件检测")
        
        # 摄像头检测标签页
        self.camera_tab = self.create_camera_tab()
        self.tab_widget.addTab(self.camera_tab, "摄像头检测")

        # 添加到主布局
        main_layout.addLayout(toolbar_layout)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.tab_widget)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def create_file_tab(self):
        """创建文件检测标签页"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # 结果显示区域
        self.image_label = QLabel("请选择图片、文件夹或视频开始检测")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid black; background-color: #f0f0f0;")
        self.image_label.setMinimumSize(640, 480)

        self.result_label = QLabel("检测结果将在这里显示")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setStyleSheet("font-size: 14px; padding: 10px;")

        layout.addWidget(self.image_label, 1)
        layout.addWidget(self.result_label)
        
        tab.setLayout(layout)
        return tab

    def create_camera_tab(self):
        """创建摄像头检测标签页"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # 摄像头组件
        self.camera_widget = CameraWidget()
        
        # 摄像头检测控制
        camera_control_layout = QHBoxLayout()
        
        self.btn_start_camera_detection = QPushButton("开始实时检测")
        self.btn_start_camera_detection.clicked.connect(self.start_camera_detection)
        
        self.btn_stop_camera_detection = QPushButton("停止实时检测")
        self.btn_stop_camera_detection.clicked.connect(self.stop_camera_detection)
        self.btn_stop_camera_detection.setEnabled(False)
        
        camera_control_layout.addWidget(self.btn_start_camera_detection)
        camera_control_layout.addWidget(self.btn_stop_camera_detection)
        camera_control_layout.addStretch()
        
        # 摄像头检测结果显示
        self.camera_result_label = QLabel("摄像头检测结果")
        self.camera_result_label.setAlignment(Qt.AlignCenter)
        self.camera_result_label.setStyleSheet("font-size: 14px; padding: 10px; border: 1px solid #ccc;")
        
        layout.addWidget(self.camera_widget)
        layout.addLayout(camera_control_layout)
        layout.addWidget(self.camera_result_label)
        
        tab.setLayout(layout)
        return tab

    def open_settings(self):
        """打开设置对话框"""
        dialog = SettingsDialog(self, self.confidence_threshold, self.iou_threshold)
        if dialog.exec_() == SettingsDialog.Accepted:
            settings = dialog.get_settings()
            self.confidence_threshold = settings['confidence']
            self.iou_threshold = settings['iou']
            QMessageBox.information(self, "设置", 
                                  f"设置已更新\n置信度: {self.confidence_threshold:.2f}\nIOU: {self.iou_threshold:.2f}")

    def select_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择图片", "", "图片文件 (*.png *.jpg *.jpeg)")
        if file_path:
            self.start_detection(file_path, False)

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if folder_path:
            self.start_detection(folder_path, False)

    def select_video(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择视频", "", "视频文件 (*.mp4 *.avi *.mov)")
        if file_path:
            self.start_detection(file_path, True)

    def start_detection(self, source, is_video):
        """开始文件检测"""
        # 禁用按钮
        self.btn_select_image.setEnabled(False)
        self.btn_select_folder.setEnabled(False)
        self.btn_select_video.setEnabled(False)
        self.btn_stop.setEnabled(True)

        # 重置UI
        self.progress_bar.setValue(0)
        self.result_label.setText("检测中...")

        # 创建并启动检测线程
        self.detection_thread = DetectionThread(
            self.detector, self.db_manager, source, is_video, False,
            self.confidence_threshold, self.iou_threshold)
        self.detection_thread.update_signal.connect(self.update_detection_result)
        self.detection_thread.finished_signal.connect(self.detection_finished)
        self.detection_thread.progress_signal.connect(self.update_progress)
        self.detection_thread.start()

    def start_camera_detection(self):
        """开始摄像头检测"""
        if not self.camera_widget.camera or not self.camera_widget.camera.isOpened():
            QMessageBox.warning(self, "警告", "请先启动摄像头")
            return
        
        # 禁用按钮
        self.btn_start_camera_detection.setEnabled(False)
        self.btn_stop_camera_detection.setEnabled(True)
        
        # 创建并启动摄像头检测线程
        camera_index = self.camera_widget.camera_combo.currentData()
        self.detection_thread = DetectionThread(
            self.detector, self.db_manager, camera_index, False, True,
            self.confidence_threshold, self.iou_threshold)
        self.detection_thread.update_signal.connect(self.update_camera_detection_result)
        self.detection_thread.finished_signal.connect(self.camera_detection_finished)
        self.detection_thread.start()

    def stop_camera_detection(self):
        """停止摄像头检测"""
        if self.detection_thread:
            self.detection_thread.stop()
            self.detection_thread.wait()
            self.camera_detection_finished()

    def stop_detection(self):
        if self.detection_thread:
            self.detection_thread.stop()
            self.detection_thread.wait()
            self.detection_finished()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_detection_result(self, data):
        """更新文件检测结果"""
        if data['type'] == 'image':
            # 显示图片检测结果
            image = cv2.imread(data['path'])
            self.draw_detections(image, [data['detection']])

            # 更新结果文本
            detection = data['detection']
            text = (f"种类: {detection['sort']} (置信度: {detection['sort_confidence']:.2f})\n"
                    f"成熟度: {detection['maturity']} (置信度: {detection['maturity_confidence']:.2f})\n"
                    f"状态: {detection['status']}")
            self.result_label.setText(text)

        elif data['type'] == 'video_frame':
            # 显示视频帧检测结果
            self.draw_detections(data['frame'], [data['detection']])

    def update_camera_detection_result(self, data):
        """更新摄像头检测结果"""
        if data['type'] == 'camera_frame':
            if data['detection']:
                # 有检测结果
                self.draw_camera_detections(data['frame'], [data['detection']])
                
                detection = data['detection']
                text = (f"种类: {detection['sort']} (置信度: {detection['sort_confidence']:.2f})\n"
                        f"成熟度: {detection['maturity']} (置信度: {detection['maturity_confidence']:.2f})\n"
                        f"状态: {detection['status']}")
                self.camera_result_label.setText(text)
            else:
                # 没有检测结果，只显示原始帧
                self.draw_camera_detections(data['frame'], [])
                self.camera_result_label.setText("未检测到榴莲")

    def draw_detections(self, image, detections):
        """绘制检测结果到文件检测标签页"""
        for detection in detections:
            bbox = detection['bbox']
            sort = detection['sort']
            maturity = detection['maturity']
            status = detection['status']

            # 绘制边界框
            x1, y1, x2, y2 = map(int, bbox)
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # 添加标签
            label = f"{sort} | {maturity} | {status}"
            cv2.putText(image, label, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # 转换为QPixmap并显示
        height, width, channel = image.shape
        bytes_per_line = 3 * width
        q_img = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
        self.image_label.setPixmap(QPixmap.fromImage(q_img).scaled(
            self.image_label.width(), self.image_label.height(),
            Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def draw_camera_detections(self, image, detections):
        """绘制检测结果到摄像头检测标签页"""
        for detection in detections:
            bbox = detection['bbox']
            sort = detection['sort']
            maturity = detection['maturity']
            status = detection['status']

            # 绘制边界框
            x1, y1, x2, y2 = map(int, bbox)
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # 添加标签
            label = f"{sort} | {maturity} | {status}"
            cv2.putText(image, label, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # 转换为QPixmap并显示到摄像头组件
        rgb_frame = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        
        pixmap = QPixmap.fromImage(qt_image)
        scaled_pixmap = pixmap.scaled(self.camera_widget.camera_label.size(), 
                                    Qt.KeepAspectRatio, 
                                    Qt.SmoothTransformation)
        self.camera_widget.camera_label.setPixmap(scaled_pixmap)

    def detection_finished(self):
        """文件检测完成"""
        # 启用按钮
        self.btn_select_image.setEnabled(True)
        self.btn_select_folder.setEnabled(True)
        self.btn_select_video.setEnabled(True)
        self.btn_stop.setEnabled(False)

        self.result_label.setText("检测完成!")

    def camera_detection_finished(self):
        """摄像头检测完成"""
        # 启用按钮
        self.btn_start_camera_detection.setEnabled(True)
        self.btn_stop_camera_detection.setEnabled(False)
        
        self.camera_result_label.setText("摄像头检测已停止")

    def closeEvent(self, event):
        """关闭事件"""
        if self.detection_thread and self.detection_thread.isRunning():
            self.detection_thread.stop()
            self.detection_thread.wait()
        self.db_manager.close()
        event.accept()