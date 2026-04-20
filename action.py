import pyautogui
import random
import time


def click(pos):
    x, y = pos

    x += random.randint(-5, 5)
    y += random.randint(-5, 5)

    pyautogui.moveTo(x, y, duration=random.uniform(0.2, 0.5))
    pyautogui.click()

    time.sleep(random.uniform(0.5, 1.0))