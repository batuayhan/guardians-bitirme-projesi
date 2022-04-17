from imutils.object_detection import non_max_suppression
import numpy as np
import cv2
import requests
import imutils

def paperControl(image_name, east, min_confidence, width, height):
	camera = cv2.VideoCapture(0)
	while True:
		#url = "http://192.168.1.20:8080/shot.jpg"
		#img_resp = requests.get(url)
		#img_arr = np.array(bytearray(img_resp.content), dtype=np.uint8)
		#image = cv2.imdecode(img_arr, -1)
		#image = imutils.resize(image, width=1000, height=1800)
		_,image = camera.read()
		cv2.imshow('Paper Check', image)
		if cv2.waitKey(1) & 0xFF == ord('s'):
			cv2.imwrite(image_name, image)
			break
	image = cv2.imread(image_name)
	orig = image.copy()
	(H, W) = image.shape[:2]
	(newW, newH) = (width, height)
	rW = W / float(newW)
	rH = H / float(newH)
	image = cv2.resize(image, (newW, newH))
	(H, W) = image.shape[:2]
	layerNames = [
		"feature_fusion/Conv_7/Sigmoid",
		"feature_fusion/concat_3"]
	net = cv2.dnn.readNet(east)
	blob = cv2.dnn.blobFromImage(image, 1.0, (W, H),
		(123.68, 116.78, 103.94), swapRB=True, crop=False)
	net.setInput(blob)
	(scores, geometry) = net.forward(layerNames)
	(numRows, numCols) = scores.shape[2:4]
	rects = []
	confidences = []
	for y in range(0, numRows):
		scoresData = scores[0, 0, y]
		xData0 = geometry[0, 0, y]
		xData1 = geometry[0, 1, y]
		xData2 = geometry[0, 2, y]
		xData3 = geometry[0, 3, y]
		anglesData = geometry[0, 4, y]
		for x in range(0, numCols):
			if scoresData[x] < min_confidence:
				continue
			(offsetX, offsetY) = (x * 4.0, y * 4.0)
			angle = anglesData[x]
			cos = np.cos(angle)
			sin = np.sin(angle)
			h = xData0[x] + xData2[x]
			w = xData1[x] + xData3[x]
			endX = int(offsetX + (cos * xData1[x]) + (sin * xData2[x]))
			endY = int(offsetY - (sin * xData1[x]) + (cos * xData2[x]))
			startX = int(endX - w)
			startY = int(endY - h)
			rects.append((startX, startY, endX, endY))
			confidences.append(scoresData[x])
	boxes = non_max_suppression(np.array(rects), probs=confidences)
	for (startX, startY, endX, endY) in boxes:
		startX = int(startX * rW)
		startY = int(startY * rH)
		endX = int(endX * rW)
		endY = int(endY * rH)
		# draw the bounding box on the image
		cv2.rectangle(orig, (startX, startY), (endX, endY), (0, 255, 0), 2)
	# show the output image
	cv2.imshow("Text Detection", orig)
	cv2.waitKey(0)
	camera.release()
	cv2.destroyAllWindows()
paperControl("papertest.jpg", "frozen_east_text_detection.pb", 0.5, 320, 320)
