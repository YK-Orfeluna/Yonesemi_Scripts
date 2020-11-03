# -*- python2.7 -*
# -*- coding: utf-8 -*

import cv2
import numpy as np

SRC = "image/lena.jpg"
CASCADE = "cascade/haarcascade_frontalface_default.xml"
MAG = 0.2

image = cv2.imread(SRC)								# 画像の取得
image_face = image.copy()							# 顔認識結果描画用

cascade = cv2.CascadeClassifier(CASCADE)			# 顔探索用のカスケード型分類器を取得
face = cascade.detectMultiScale(image, 1.1, 3)		# 顔探索(画像,縮小スケール,最低矩形数)

for (x, y, w, h) in face:							# 顔検出した部分を赤い四角形で囲う
	cv2.rectangle(image_face, (x, y),(x + w, y + h),(0, 0, 255), 3)

#ROI(Region Of Interest: 関心領域)
x, y, w, h = face[0]								# 顔領域左上の座標(x, y)と領域の長さ(w, h)
length = (w+h)/2									# 顔領域の長さ
th = int(length * MAG)								# length*MAGの分だけ，顔領域を拡大
x1 = x - th											# 拡大後の顔領域の左上(x1, y1)，右下（x2, y2
x2 = x+w+th
y1 = y - th
y2 = y+h+th
roi = image[y1:y2, x1:x2]							# ROIを作成する
roi = cv2.resize(roi, (300, 300))

# ROIの範囲を緑の四角形で囲んでおく
cv2.rectangle(image_face, (x1, y1),(x2, y2),(0, 255, 0), 3)

cv2.imshow("result", image_face)					# 画像表示
cv2.imshow("ROI", roi)

cv2.waitKey(0)										# キー入力待機

cv2.imwrite("image/face_search.jpg", image_face)	# 画像保存

cv2.destroyAllWindows()								# 全ウィンドウ破棄
exit()