# -*- coding: utf-8 -*-
import os
import sys
import configparser

def get_script_dir():
    """兼容直接运行和 PyInstaller 打包后的路径获取"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

# 确定基础路径
BASE_DIR = get_script_dir()
RESOURCE_DIR = os.path.join(BASE_DIR, "images")
INI_PATH = os.path.join(BASE_DIR, "config.ini")

# 初始化解析器
config = configparser.ConfigParser()

# 如果配置文件不存在，自动创建一个默认的，防止程序闪退
if not os.path.exists(INI_PATH):
    config['Game'] = {'window_title': '游戏窗口', 'window_class': 'Win32Window'}
    config['Match'] = {'sift_match_threshold': '0.75', 'min_match_count': '45'}
    config['AntiBan'] = {'click_offset_max': '9', 'move_duration_min': '0.4', 'move_duration_max': '0.9'}
    with open(INI_PATH, 'w', encoding='utf-8') as configfile:
        config.write(configfile)
else:
    config.read(INI_PATH, encoding='utf-8')

# --- 导出给其他模块使用的全局变量 ---

# 游戏窗口配置（字符串）
WINDOW_TITLE = config.get('Game', 'window_title', fallback='游戏窗口')
WINDOW_CLASS = config.get('Game', 'window_class', fallback='Win32Window')

# SIFT 匹配阈值（转换为浮点数和整数）
SIFT_MATCH_THRESHOLD = config.getfloat('Match', 'sift_match_threshold', fallback=0.75)
MIN_MATCH_COUNT = config.getint('Match', 'min_match_count', fallback=45)

# 模拟参数（转换为浮点数和整数）
CLICK_OFFSET_MAX = config.getint('AntiBan', 'click_offset_max', fallback=9)
MOVE_DURATION_MIN = config.getfloat('AntiBan', 'move_duration_min', fallback=0.4)
MOVE_DURATION_MAX = config.getfloat('AntiBan', 'move_duration_max', fallback=0.9)