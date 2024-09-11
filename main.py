import os
import random
import sys
import time
import cv2
import numpy as np
import pyautogui
import win32gui
import win32com.client as client
from PyQt5.QtWidgets import QApplication

# 创建 SIFT 对象和 Shell 对象
SIFT = cv2.SIFT_create()
shell = client.Dispatch('WScript.Shell')


def get_app_shot(hwnd):
    """获取指定窗口的截图并转换为 numpy 数组。"""
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    app = QApplication.instance() or QApplication(sys.argv)
    screen = QApplication.primaryScreen()
    image = screen.grabWindow(hwnd).toImage()

    # QImage 转换为 numpy 数组
    width, height = image.width(), image.height()
    buf = image.bits()
    buf.setsize(height * width * 4)
    arr = np.frombuffer(buf, np.uint8).reshape((height, width, 4))

    return cv2.cvtColor(arr, cv2.COLOR_BGR2BGRA), left, top


def compute_keypoints_descriptors(image):
    """计算图像的关键点和描述符。"""
    return SIFT.detectAndCompute(image, None)


def locate_image(target_image, kp_des_screen):
    """在屏幕截图中查找目标图像的位置。"""
    kp_screen, des_screen = kp_des_screen
    kp_target, des_target = SIFT.detectAndCompute(target_image, None)

    if des_screen is None or des_target is None:
        return None

    # 使用 FLANN 匹配器进行匹配
    flann = cv2.FlannBasedMatcher()
    matches = flann.knnMatch(des_target, des_screen, k=2)

    # 使用比率测试来找到好的匹配点
    good_matches = [m for m, n in matches if m.distance < 0.75 * n.distance]

    if len(good_matches) > 45:
        src_pts = np.float32([kp_target[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp_screen[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        mm, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

        if mm is not None:
            h, w = target_image.shape[:2]
            pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
            dst = cv2.perspectiveTransform(pts, mm)
            mid_pos = tuple(np.mean([dst[0][0], dst[2][0]], axis=0))
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


def automatic_clicks(cycles, delay, target_files):
    """自动化点击循环，根据指定的次数和延迟进行操作。"""
    hwnd0 = win32gui.FindWindow('Win32Window', '游戏窗口名')
    hwnd1 = win32gui.FindWindowEx(0, hwnd0, 'Win32Window', '游戏窗口名')

    if hwnd0 == 0:
        print('未找到游戏窗口，退出。')
        return

    hwnd = hwnd0
    for i in range(cycles):
        screen, left, top = get_app_shot(hwnd)
        kp_des_screen = compute_keypoints_descriptors(screen)

        for image_name, image in target_files.items():
            pos = locate_image(image, kp_des_screen)
            if pos:
                shell.SendKeys('%')
                win32gui.SetForegroundWindow(hwnd)
                click_position(pos, left, top)

                if image_name == "1" and hwnd == hwnd0:
                    print(f'第 {i + 1:03d} 次挑战')
                    time.sleep(delay)
                    break

        hwnd = hwnd1 if hwnd == hwnd0 and hwnd1 != 0 else hwnd0


if __name__ == '__main__':
    try:
        times = int(input('输入循环次数：'))
        waiting_time = int(input('输入循环间隔（秒）：'))
        script_path = os.path.abspath(sys.argv[0])
        resource_folder = os.path.join(os.path.dirname(script_path), "images")

        # 加载资源文件夹中的图片
        files = {}
        for image_file in os.listdir(resource_folder):
            if image_file.lower().endswith(('.png', '.jpg', '.jpeg')):
                file_path = os.path.join(resource_folder, image_file)
                image_name = os.path.splitext(image_file)[0]
                image = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)

                if image is not None:
                    files[image_name] = image
                else:
                    print(f"无法加载图像：{file_path}")

        automatic_clicks(times, waiting_time, files)

    except ValueError:
        print('输入异常，请重试...')
    except Exception as e:
        print(f"程序遇到错误：{e}")
