# -*- coding: utf-8 -*

import numpy as np
import cv2
from mahotas.features import surf

def face_roi(face, mag=0.4, normal=200) :
	# magは顔領域の拡大率，normalは正規化後のウィンドウサイズ
	global frame, face_pre
	face_pre = face.copy()
	x, y, w, h = face[0]
	
	length = (w+h)/2
	th = 0#int(round(length * mag, 0))	# roundで四捨五入

	# 左上が(x1, y1)，右上が(x2, y2)
	x1 = x - th
	x2 = x+w+th
	y1 = y - th
	y2 = y+h+th

	# 顔付近をROIで抜き出す
	roi = frame[y1:y2, x1:x2]	# 上から下，左から右（どちらも数値の小さい方から大きい方へ）
	print(roi.shape)
	# ROIの大きさを正規化する
	"""
	if w != h :
		normal_y = h * (normal / w)
	else :
		normal_y = normal
	"""
	normal_y = normal
	dsize = (normal, normal_y)
	out = cv2.resize(roi, dsize)

	return out

# ヒストグラムの最大値と最小値は，あらかじめ全ての学習用データに対してSURF抽出とその中の最大値・最小値の調査を行っておく
def surf_hist(image) :
	result = np.array([])													# 結果格納用の配列（空）

	descriptors = surf.surf(image, descriptor_only=True)					# SURFの抜き出し
	#descriptors = surf.dense(image, spacing=16)
	maxi = descriptors.max()												# ヒストグラム作成のための最小値と最大値
	mini = descriptors.min()
	for i in descriptors :
		hist = np.histogram(i, bins=10, range=(mini, maxi), density=True)	# ヒストグラム作成(ヒストグラム，ラベルデータ)
		result = np.append(result, hist[0])									# resultにヒストグラムを追加する
	return result

# 表示用ウィンドウの名前
WINDOW_NAME = "dst"
cv2.namedWindow(WINDOW_NAME)

# ファイルを読み込む場合はファイル名，webカメラなら0
#VIDEO = 0
VIDEO = "test.mov"
src = cv2.VideoCapture(VIDEO)
ret, frame = src.read()

if ret == False :
	if VIDEO == 0 :
		exit("Camera is None")
	else :
		exit("Video / Camera is None")

frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

# 読み込むカスケードファイルの名前
CASCADE = "cascade/haarcascade_frontalface_default.xml"
cascade = cv2.CascadeClassifier(CASCADE)

face_pre = np.array([[0, 0, 100, 100]])

#img = cv2.imread("lena.jpg", 2)
img = cv2.resize(frame, (100, 100))
print(surf_hist(img).shape)

# 顔の大きさの閾値
mini = 160
maxi = 230
face_flag = -1

while True :
	# retは読み込み成功判別，frameに動画の1フレームが格納される
	ret, frame = src.read()

	# 終了処理に必要
	if frame is None :
		break
	frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
	
	# 顔認識
	face = cascade.detectMultiScale(frame, 1.1, 3)
	#print face

	if len(face) == 1 :
		if mini < face[0][2] < maxi :		# 顔の大きさが閾値に収まるか判定
			frame = face_roi(face)
		else :
			face_flag = -1

	elif len(face) > 1 and face_flag != -1:
		f = (maxi + mini) / 2				# 抽出すべき顔の長さの理想値
		for x, i in enumerate(face) :
			if x == 0 :						# for文1回目なので，無条件にf_outとf_difを定める
				f_out = i[2]				# 検出された物の長さ
				f_dif = abs(f - f_out)		# f_outとfの絶対値
				f_x = x						# 検出された物の順番
			else :							# for文2回目以降
				f_dif2 = abs(f - i[2])		# 検出された物とfの絶対値
				if f_dif > f_dif2 :			# f_dif > f_dif2: 新しい物の方が理想値に近い
					f_out = i[2]			# 理想値に近い方を顔とする
					f_dif = f_dif2
					f_x = x
		face = face[f_x]

		if mini < face[2] < maxi :			# 検索した顔の大きさが閾値に収まるか反転
			face = np.array([face])
			frame = face_roi(face)
		else :
			face_flag = -1

	if len(face) == 0 or face_flag == -1 :
		frame = face_roi(face_pre)

	face_flag = 0

	surf_result = surf_hist(frame)

	cv2.imshow(WINDOW_NAME, frame)
	key = cv2.waitKey(1000)
	if key != -1 :
		exit()