# -*- coding:utf-8 -*-
import os
import random
import sys
import time
from typing import Any

import numpy
import numpy as np
import pyautogui
import win32gui
import win32com.client as client
import cv2.cv2 as cv2
import tkinter as tk

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QImage

left, top = 0, 0
SIFT = cv2.SIFT_create()
shell = client.Dispatch('WScript.Shell')


def load_images():
    obj = {}
    path = os.getcwd() + '/images'
    file_list = os.listdir(path)

    for file in file_list:
        name = file.split('.')[0]
        file_path = path + '/' + file
        a = cv2.imread(file_path, cv2.COLOR_BGR2BGRA)
        obj[name] = a

    return obj


def insert_text(area, text):
    area.configure(state=tk.NORMAL)
    area.insert(tk.END,
                time.strftime('%H:%M:%S',
                              time.localtime(time.time())) + ' ' + text + '\n')
    area.configure(state=tk.DISABLED)
    area.see(tk.END)


def get_app_shot(hwnd):

    global left, top

    # 单应用截图
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    app = QApplication(sys.argv)
    screen = QApplication.primaryScreen()
    image = screen.grabWindow(hwnd).toImage()

    # QImage to MAT(numpy array)
    image = image.convertToFormat(QImage.Format_RGBA8888)
    width = image.width()
    height = image.height()
    ptr = image.bits()
    ptr.setsize(height * width * 4)
    arr = np.frombuffer(ptr, np.uint8).reshape((height, width, 4))

    image = cv2.cvtColor(numpy.asarray(arr), cv2.COLOR_BGR2BGRA)

    return image


def compute_app_shot(screen):
    kp2, des2 = SIFT.detectAndCompute(screen, None)
    return kp2, des2


def get_location(image, kp, des):
    MIN_MATCH_COUNT = 45
    FLANN_INDEX_TREE = 0

    # 用SIFT找到关键点和描述符
    kp2, des2 = SIFT.detectAndCompute(image, None)

    index_params = dict(algorithm=FLANN_INDEX_TREE, trees=5)
    search_params = dict(checks=50)

    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(des2, des, k=2)

    good = []
    for m, n in matches:
        if m.distance < 0.75 * n.distance:
            good.append(m)

    if len(good) > MIN_MATCH_COUNT:
        src_pts = np.float32([kp2[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        matchesMask = mask.ravel().tolist()
        h, w = image.shape
        pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
        if M is not None:
            dst = cv2.perspectiveTransform(pts, M)
            arr = np.int32(dst)
            midPosArr = arr[0] + (arr[2] - arr[0]) // 2
            midPos = (midPosArr[0][0], midPosArr[0][1])
            return midPos
        else:
            return None
    else:
        return None


def click_it(target_position):
    factor = random.randint(0, 3)
    x, y = random.randint(-factor, factor), random.randint(-factor, factor)
    newPos = (target_position[0] + x + left, target_position[1] + y + top + 10)
    pyautogui.moveTo(newPos, duration=0.2 * random.randint(3, 5))
    pyautogui.click()
    if factor % 2 >= 0:
        time.sleep(random.randint(300,800)/1000)
        pyautogui.click()

    time.sleep(random.randint(1000, 2000)/1000)


class Mitama:
    def __init__(self):
        self._flag = False

    def run(self, area):
        image = load_images()
        insert_text(area, '开始挑战')

        hwnd = win32gui.FindWindow('Win32Window', '阴阳师-网易游戏')
        hwne = win32gui.FindWindowEx(0, hwnd, 'Win32Window', '阴阳师-网易游戏')
        hwnc = hwnd
        waiting = False
        num, count = 1, 1
        images = {
            '1',
            '2',
            '3',
            '4',
            '5',
            '0',
        }

        while self._flag is not True:
            count += 1
            kp, des = [Any, Any]

            if hwne != 0:
                if count%2 == 0:
                    hwnc = hwnd
                else:
                    hwnc = hwne

            screen = get_app_shot(hwnc)

            window_shape = screen.shape
            kp, des = compute_app_shot(screen)

            for i in list(images):
                pos = get_location(image[i], kp, des)
                if pos is not None:
                    if i == '3':
                        if hwne != 0:
                            if count % 2 == 0:
                                insert_text(area, '第' + str(num) + '轮结束')
                        else:
                            insert_text(area, '第' + str(num) + '轮结束')

                        num += 1

                    shell.SendKeys('%')
                    win32gui.SetForegroundWindow(hwnc)
                    click_it(pos)
                    break

    def terminate(self):
        self._flag = True
