import os


class Config:
    # 模型路径
    SORT_MODEL_PATH = r"E:\迅雷下载\yolov8-main\yolov8-main\durian_train\runs\train\durian_sort\weights\best.pt"
    MATURITY_MODEL_PATH = r"E:\迅雷下载\yolov8-main\yolov8-main\durian_train\runs\train\durian_murturity\weights\best.pt"

    # 种类类别
    SORT_CLASSES = ['bawor', 'black thorn', 'kanyao', 'monthong', 'musang king', 'not durian']

    # 成熟度类别
    MATURITY_CLASSES = ['defective', 'immature', 'mature']

    # 成熟度对应的状态
    MATURITY_STATUS = {
        'defective': '该丢弃',
        'immature': '待发',
        'mature': '急发'
    }

    # 数据库配置
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': '123456',
        'database': 'durian_detection',
        'port': 3306
    }


config = Config()