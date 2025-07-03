import os
from datetime import datetime

def get_current_time_str():
    """获取当前时间字符串"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def ensure_dir(directory):
    """确保目录存在，不存在则创建"""
    if not os.path.exists(directory):
        os.makedirs(directory)