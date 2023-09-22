import os
import random
import sys
import win32com.client as client
import win32gui
import time

import cv2
import numpy as np
import pyautogui

from PyQt5.QtWidgets import QApplication

SIFT = cv2.SIFT_create()
shell = client.Dispatch('WScript.Shell')


def get_app_shot(hwnd):
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    app = QApplication(sys.argv)
    screen = QApplication.primaryScreen()
    image = screen.grabWindow(hwnd).toImage()

    # QImage to numpy array
    width = image.width()
    height = image.height()
    buf = image.bits()
    buf.setsize(height * width * 4)
    arr = np.frombuffer(buf, np.uint8).reshape((height, width, 4))

    return cv2.cvtColor(arr, cv2.COLOR_BGR2BGRA), left, top


def compute_app_shot(screen):
    kp, des = SIFT.detectAndCompute(screen, None)
    return kp, des


def location(image, kp, des):
    kp2, des2 = SIFT.detectAndCompute(image, None)

    flann = cv2.FlannBasedMatcher()
    matches = flann.knnMatch(des2, des, k=2)

    good = [m for m, n in matches if m.distance < 0.75 * n.distance]

    if len(good) > 45:
        src_pts = np.float32([kp2[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
        mm, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        mask.ravel().tolist()

        if mm is not None:
            h, w = image.shape[:2]
            pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
            dst = cv2.perspectiveTransform(pts, mm)
            mid_pos_arr = dst[0] + (dst[2] - dst[0]) // 2
            mid_pos = (mid_pos_arr[0][0], mid_pos_arr[0][1])
            return mid_pos

    return None


def click(pos, left, top):

    # 随机偏移量
    factor = random.randint(0, 9)

    # 随机偏移坐标
    x, y = random.randint(-factor, factor), random.randint(-factor, factor)

    # UI 的特殊性向下偏移 10px
    new_pos = (pos[0] + left + x, pos[1] + top + y + 10)

    # 随机移动速度
    duration = random.uniform(0.4, 0.9)
    pyautogui.moveTo(new_pos, duration=duration)
    pyautogui.click()

    if factor % 2 == 0:
        # 不固定的第二次点击间隔
        time.sleep(random.uniform(0.3, 0.8))
        pyautogui.click()

    # 响应等待
    time.sleep(random.uniform(0.5, 1.0))


def automatic(arg):
    hwnd = None
    hwnd0 = win32gui.FindWindow('Win32Window', '阴阳师-网易游戏')
    hwnd1 = win32gui.FindWindowEx(0, hwnd0, 'Win32Window', '阴阳师-网易游戏')

    if hwnd0 == 0:
        print('未找到游戏窗口，退出。')
        return
    elif hwnd1 == 0:
        print('未找到第二个游戏窗口，单人模式...')

    i = 0
    while i < arg:
        if hwnd is None:
            hwnd = hwnd0
        elif hwnd1 != 0 and hwnd is hwnd0:
            hwnd = hwnd1
        else:
            hwnd = hwnd0

        screen, left, top = get_app_shot(hwnd)
        window_shape = screen.shape
        kp, des = compute_app_shot(screen)

        for _, image in files.items():
            pos = location(image, kp, des)
            if pos is not None:
                shell.SendKeys('%')
                win32gui.SetForegroundWindow(hwnd)
                click(pos, left, top)
                if _ == "1" and hwnd is hwnd0:
                    i += 1
                    print(f'第 {i:03d} 次挑战')

                break


if __name__ == '__main__':
    try:
        times = int(input('输入循环次数：'))
        files = {}
        script_path = sys.argv[0]
        script_dir = os.path.dirname(script_path)
        resource_folder = os.path.join(script_dir, "images")
        file_list = os.listdir(resource_folder)

        for image_file in file_list:
            ifile = os.path.join(resource_folder, image_file)
            name = image_file.split('.')[0]
            bgr = cv2.imread(ifile, cv2.COLOR_BGR2BGRA)
            files[name] = bgr

        automatic(times)
    except ValueError:
        print('输入异常，请重试...')
