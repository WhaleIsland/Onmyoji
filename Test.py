# -*- coding:utf-8 -*-
import os
import cv2.cv2 as cv2
import numpy as np

from matplotlib import pyplot as plt

SIFT = cv2.SIFT_create()

def test():
    path = os.getcwd() + '/testImages'
    queryImage = path + '/queryImage.jpg'
    trainingImage = path + '/trainingImage.jpg'
    image1 = cv2.imread(queryImage, cv2.COLOR_BGR2BGRA)
    image2 = cv2.imread(trainingImage, cv2.COLOR_BGR2BGRA)
    kp1, des1 = SIFT.detectAndCompute(image1, None)
    kp2, des2 = SIFT.detectAndCompute(image2, None)

    index_params = dict(algorithm=0, trees=5)
    search_params = dict(checks=50)

    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(des2, des1, k=2)

    good = []
    for m, n in matches:
        if m.distance < 0.75 * n.distance:
            good.append(m)

    resultImage = cv2.drawMatchesKnn(image1, kp1, image2, kp2, matches, image2,flags=2)

    plt.imshow(resultImage, ), plt.show()

    # 显示匹配后图像
    cv2.imshow("resultImage", resultImage)
    cv2.waitKey()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    test()