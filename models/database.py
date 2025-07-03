import mysql.connector
from mysql.connector import Error
from durian_detection_system.config.settings import config


class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.connect()
        self._create_table_if_not_exists()

    def connect(self):
        """连接到MySQL数据库"""
        try:
            self.connection = mysql.connector.connect(**config.DB_CONFIG)
            if self.connection.is_connected():
                print("成功连接到MySQL数据库")
        except Error as e:
            print(f"连接MySQL数据库错误: {e}")
            raise

    def _create_table_if_not_exists(self):
        """创建表如果不存在"""
        create_table_query = """
        CREATE TABLE IF NOT EXISTS durian_detections (
            id INT AUTO_INCREMENT PRIMARY KEY,
            image_path VARCHAR(255) NOT NULL,
            sort VARCHAR(50) NOT NULL,
            sort_confidence FLOAT NOT NULL,
            maturity VARCHAR(50) NOT NULL,
            maturity_confidence FLOAT NOT NULL,
            status VARCHAR(50) NOT NULL,
            detection_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            bbox_x1 FLOAT,
            bbox_y1 FLOAT,
            bbox_x2 FLOAT,
            bbox_y2 FLOAT
        )
        """

        try:
            cursor = self.connection.cursor()
            cursor.execute(create_table_query)
            self.connection.commit()
            cursor.close()
        except Error as e:
            print(f"创建表错误: {e}")
            raise

    def save_detection(self, image_path, detection):
        """保存检测结果到数据库"""
        insert_query = """
        INSERT INTO durian_detections (
            image_path, sort, sort_confidence, maturity, maturity_confidence, 
            status, bbox_x1, bbox_y1, bbox_x2, bbox_y2
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        # 处理可能的NULL值
        maturity = detection.get('maturity', 'unknown')  # 默认值
        maturity_confidence = detection.get('maturity_confidence', 0.0)  # 默认值

        try:
            cursor = self.connection.cursor()
            cursor.execute(insert_query, (
                image_path,
                detection['sort'],
                detection['sort_confidence'],
                maturity,  # 使用处理后的值
                maturity_confidence,
                detection.get('status', 'unknown'),  # 默认值
                detection['bbox'][0],
                detection['bbox'][1],
                detection['bbox'][2],
                detection['bbox'][3]
            ))
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"保存检测结果错误: {e}")
            return False

    def close(self):
        """关闭数据库连接"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL连接已关闭")