# -*- coding: utf-8 -*
# mahotasによるSURF抽出

import numpy as np
import cv2
from mahotas.features import surf

img = cv2.imread("image/lena.jpg", 2)						#　画像の読み込み
img = cv2.resize(img, (100, 100))					# 画像のリサイズ（正規化のため）

descriptors = surf.surf(img, descriptor_only=True)	# descriptorsの抽出
print("number of SURF: %s" %len(descriptors))

maxi = descriptors.max()							# histogram作成のための最大値と最小値
mini = descriptors.min()							

for d in descriptors :								# 各特徴量をhistogram化
	hist, label = np.histogram(descriptors, bins=10, range=(mini, maxi), density=True)
	print(hist)