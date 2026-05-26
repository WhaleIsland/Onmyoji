# -*- coding: utf-8 -*-
import os
import cv2
import time
import random
import pyautogui
import config
from utils.window_control import find_game_windows, get_app_shot, force_foreground
from utils.image_matcher import ImageMatcher


class OnmyojiBot:
    def __init__(self):
        self.matcher = ImageMatcher()
        self.templates = {}
        self.load_templates()

    def load_templates(self):
        """加载 images 目录下的所有模板图片"""
        if not os.path.exists(config.RESOURCE_DIR):
            print(f"错误: 未找到图片文件夹 {config.RESOURCE_DIR}")
            return

        for file_name in os.listdir(config.RESOURCE_DIR):
            if file_name.endswith(('.png', '.jpg', '.jpeg')):
                name = os.path.splitext(file_name)[0]
                path = os.path.join(config.RESOURCE_DIR, file_name)
                # 以 BGRA 格式读取以匹配截图通道
                img = cv2.imread(path, cv2.COLOR_BGR2BGRA)
                if img is not None:
                    self.templates[name] = img
        print(f"成功加载了 {len(self.templates)} 个模板图片。")

    def simulate_click(self, pos, left, top):
        """拟真鼠标点击"""
        factor = random.randint(0, config.CLICK_OFFSET_MAX)
        x_offset = random.randint(-factor, factor)
        y_offset = random.randint(-factor, factor)

        # 计算相对全屏的绝对坐标（含 10px UI 修正）
        target_x = int(pos[0] + left + x_offset)
        target_y = int(pos[1] + top + y_offset + 10)

        duration = random.uniform(config.MOVE_DURATION_MIN, config.MOVE_DURATION_MAX)
        pyautogui.moveTo((target_x, target_y), duration=duration)
        pyautogui.click()

        # 50% 概率触发双击
        if factor % 2 == 0:
            time.sleep(random.uniform(0.3, 0.8))
            pyautogui.click()

        time.sleep(random.uniform(0.5, 1.0))

    def run(self, target_count):
        """启动自动化循环"""
        hwnd0, hwnd1 = find_game_windows()

        if hwnd0 == 0:
            print('未找到游戏窗口，退出。')
            return
        elif hwnd1 == 0:
            print('未找到第二个游戏窗口，将以单人模式运行...')

        current_hwnd = None
        count = 0

        while count < target_count:
            # 双开交替轮询逻辑
            if current_hwnd is None:
                current_hwnd = hwnd0
            elif hwnd1 != 0 and current_hwnd == hwnd0:
                current_hwnd = hwnd1
            else:
                current_hwnd = hwnd0

            # 截图并提取当前窗口特征
            screen, left, top = get_app_shot(current_hwnd)
            screen_kp, screen_des = self.matcher.compute_features(screen)

            # 遍历模板匹配
            for name, template_img in self.templates.items():
                pos = self.matcher.locate_template(template_img, screen_kp, screen_des)

                if pos is not None:
                    # 激活当前窗口并点击
                    force_foreground(current_hwnd)
                    self.simulate_click(pos, left, top)

                    # 计数逻辑：如果是核心标志“1”且发生在主号窗口
                    if name == "1" and current_hwnd == hwnd0:
                        count += 1
                        print(f'第 {count:03d} / {target_count:03d} 次挑战开始')
                        time.sleep(3)
                    break  # 匹配到一个图标并点击后，跳出当前对图片的遍历，重新截图