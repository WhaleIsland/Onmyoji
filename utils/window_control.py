# -*- coding: utf-8 -*-
import sys
import cv2
import numpy as np
import win32gui
import win32com.client as client
from PyQt5.QtWidgets import QApplication
import config

# 初始化 WScript.Shell 用于激活窗口
try:
    _shell = client.Dispatch('WScript.Shell')
except Exception:
    _shell = None


def find_game_windows():
    """寻找主窗口和双开的第二个窗口"""
    hwnd0 = win32gui.FindWindow(config.WINDOW_CLASS, config.WINDOW_TITLE)
    hwnd1 = win32gui.FindWindowEx(0, hwnd0, config.WINDOW_CLASS, config.WINDOW_TITLE)
    return hwnd0, hwnd1


def force_foreground(hwnd):
    """强行将指定窗口切换到最前台"""
    if _shell:
        _shell.SendKeys('%')  # 发送 Alt 键绕过 Windows 限制
    win32gui.SetForegroundWindow(hwnd)


def get_app_shot(hwnd):
    """获取指定窗口的截图并返回 BGR 格式及窗口左上角坐标"""
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)

    # 使用 PyQt5 截图
    _app = QApplication.instance() or QApplication(sys.argv)
    screen = QApplication.primaryScreen()
    image = screen.grabWindow(hwnd).toImage()

    width = image.width()
    height = image.height()
    buf = image.bits()
    buf.setsize(height * width * 4)

    arr = np.frombuffer(buf, np.uint8).reshape((height, width, 4))
    # 转换为 OpenCV 的 BGR 格式（去掉 Alpha 通道以便进行后续处理，或保持 BGRA）
    return cv2.cvtColor(arr, cv2.COLOR_BGR2BGRA), left, top