# -*- coding: utf-8 -*-
import cv2
import numpy as np
import config


class ImageMatcher:
    def __init__(self):
        # 初始化全局 SIFT 探测器
        self.sift = cv2.SIFT_create()
        self.flann = cv2.FlannBasedMatcher()

    def compute_features(self, image):
        """计算图像的特征点和描述符"""
        return self.sift.detectAndCompute(image, None)

    def locate_template(self, template_img, screen_kp, screen_des):
        """在屏幕特征中查找模板图片的位置，返回中心点坐标"""
        kp_tpl, des_tpl = self.compute_features(template_img)

        # 如果模板本身太小或没有特征点，直接跳过
        if des_tpl is None or screen_des is None:
            return None

        matches = self.flann.knnMatch(des_tpl, screen_des, k=2)
        good = [m for m, n in matches if m.distance < config.SIFT_MATCH_THRESHOLD * n.distance]

        if len(good) > config.MIN_MATCH_COUNT:
            src_pts = np.float32([kp_tpl[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
            dst_pts = np.float32([screen_kp[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

            mm, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
            if mm is not None:
                h, w = template_img.shape[:2]
                pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
                dst = cv2.perspectiveTransform(pts, mm)

                # 计算中心点
                mid_pos_arr = dst[0] + (dst[2] - dst[0]) // 2
                return (mid_pos_arr[0][0], mid_pos_arr[0][1])
        return None