# -*- coding: utf-8 -*
# OpenCV2.4.13によるSURF抽出

import numpy as np
from numpy import histogram
import cv2

img = cv2.imread("image/lena.jpg", 2)								#　画像の読み込み
img = cv2.resize(img, (100, 100))							# 画像のリサイズ（正規化のため）

surf = cv2.SURF()											# SURF関数（クラス）の設定
keypoints, descriptors = surf.detectAndCompute(img, None)	# keypointsとdetectorsを抽出
print("number of SURF: %s" %len(descriptors))

maxi = descriptors.max()									# histogram作成のための最大値と最小値
mini = descriptors.min()

for d in descriptors :										# 各特徴量をhistogram化する
	hist, label = np.histogram(descriptors,  bins=10, range=(mini, maxi), density=True)
	print(hist)