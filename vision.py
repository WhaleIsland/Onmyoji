import os
import cv2
import numpy as np
import pyautogui


class Vision:

    def __init__(self, image_dir):
        self.templates = {}

        for file in os.listdir(image_dir):
            name = file.split(".")[0]
            path = os.path.join(image_dir, file)

            img = cv2.imread(path, 0)
            self.templates[name] = img

    def screenshot(self):
        img = pyautogui.screenshot()
        return cv2.cvtColor(np.array(img), cv2.COLOR_BGR2GRAY)

    def find(self, name, threshold=0.8):
        screen = self.screenshot()
        template = self.templates.get(name)

        if template is None:
            return None

        res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= threshold)

        if len(loc[0]) > 0:
            y, x = loc[0][0], loc[1][0]
            return (x, y)

        return None