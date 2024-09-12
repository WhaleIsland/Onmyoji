import msvcrt
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


def resource_path(relative_path):
    """获取资源文件的绝对路径（适用于打包后的环境）。"""
    if getattr(sys, 'frozen', False):
        # 如果程序是通过 PyInstaller 打包的
        base_path = os.path.dirname(sys.executable)
    else:
        # 如果程序是直接运行的源代码
        base_path = os.path.dirname(__file__)

    return os.path.join(base_path, relative_path)


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


def click_position(pos, left, top):
    """在指定位置点击，并添加随机偏移和延迟。"""
    x_offset, y_offset = random.randint(-9, 9), random.randint(-9, 9)
    new_pos = (pos[0] + left + x_offset, pos[1] + top + y_offset + 10)

    # 根据距离计算移动时间
    current_pos = pyautogui.position()
    distance = np.linalg.norm(np.array(new_pos) - np.array(current_pos))
    duration = distance * random.uniform(0.8, 1.2) / 2048

    pyautogui.moveTo(new_pos, duration=duration, tween=pyautogui.easeInOutQuad)
    pyautogui.click()

    # 随机触发第二次点击
    if random.randint(0, 9) % 2 == 0:
        time.sleep(random.uniform(0.3, 0.8))
        pyautogui.click()

    time.sleep(random.uniform(0.5, 1.0))


def find_multiple_windows(title):
    """查找所有匹配指定标题的窗口句柄。"""
    hwnd_list = []

    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd) and title in win32gui.GetWindowText(hwnd):
            hwnd_list.append(hwnd)

    win32gui.EnumWindows(callback, None)
    return hwnd_list


def automatic(times, delay):
    """自动化点击循环，在多个窗口之间切换操作。"""
    hwnds = find_multiple_windows('游戏窗口名')

    if not hwnds:
        print('未找到游戏窗口，退出...')
        time.sleep(5)
        return

    current_window_index = 0
    i = 1
    while i < times:
        start_time = time.time()

        while time.time() - start_time < 30:
            hwnd = hwnds[current_window_index]
            screen, left, top = get_app_shot(hwnd)
            window_shape = screen.shape
            kp, des = compute_app_shot(screen)

            for _, image in files.items():
                pos = location(image, kp, des)
                if pos is not None:
                    start_time = time.time()
                    shell.SendKeys('%')
                    win32gui.SetForegroundWindow(hwnd)
                    click_position(pos, left, top)
                    if _ == "1" and hwnd is hwnds[0]:
                        print(f'第 {i + 1:03d} 次挑战')
                        i += 1
                        time.sleep(delay)
                    break

            # 切换到下一个窗口
            current_window_index = (current_window_index + 1) % len(hwnds)
        else:
            print(f"第 {i:03d} 次未找到目标图像，退出。")
            return


if __name__ == '__main__':
    try:
        times = int(input('输入循环次数：'))
        waiting_time = int(input('输入循环间隔（秒）：'))
        files = {}
        resource_folder = resource_path("images")
        file_list = os.listdir(resource_folder)

        for image_file in file_list:
            ifile = os.path.join(resource_folder, image_file)
            name = image_file.split('.')[0]
            bgr = cv2.imread(ifile, cv2.IMREAD_UNCHANGED)
            files[name] = bgr

        automatic(times, waiting_time)
    except ValueError:
        print('输入异常，请重试...')
    except Exception as e:
        print(f"程序遇到错误：{e}")
    finally:
        sys.exit()
