
	# import the necessary packages
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
from imutils.video import VideoStream
import numpy as np
import imutils
import time
import cv2
import os
import pyttsx3
import telegram
import requests
import telebot
import datetime
TOKEN = '1298850920:AAFstj1rll9LuhWALI6Iunb6lxQ_lTv-SDs'

bot = telegram.Bot(TOKEN)
bot1 = telebot.TeleBot(TOKEN)
x=1
y = 1
y1 =1
counter2 = 11
start2 = time.time()
counter3 = 5
start3 = time.time()
link =""
engine= pyttsx3.init()
""" RATE"""
rate = engine.getProperty('rate')   # getting details of current speaking rate
print (rate)                        #printing current voice rate
engine.setProperty('rate', 125)
@bot1.message_handler(commands=['finish'])
def send_welcome(message):
	bot1.reply_to(message,'ok thank you')
	bot1.stop_polling()

def send_msg_tsg(text):
	chat_id = "732053544"
	bot.send_message(chat_id, text)
	bot.send_photo(chat_id=chat_id, photo=open('tersangka.png', 'rb'))
	bot.send_message(chat_id,"if the suspect doesn't wear a mask please click /Yes if the suspect wearing a mask click /No" )
def send_msg(text):
    chat_id = "732053544"
    bot.send_message(chat_id, text)
    
def detect_and_predict_mask(frame, faceNet, maskNet):
	# grab the dimensions of the frame and then construct a blob
	# from it
	(h, w) = frame.shape[:2]
	blob = cv2.dnn.blobFromImage(frame, 1.0, (224, 224),
		(104.0, 177.0, 123.0))
	
	# pass the blob through the network and obtain the face detections
	faceNet.setInput(blob)
	detections = faceNet.forward()
	print(detections.shape)

	# initialize our list of faces, their corresponding locations,
	# and the list of predictions from our face mask network
	faces = []
	locs = []
	preds = []

	# loop over the detections
	for i in range(0, detections.shape[2]):
		# extract the confidence (i.e., probability) associated with
		# the detection
		confidence = detections[0, 0, i, 2]

		# filter out weak detections by ensuring the confidence is
		# greater than the minimum confidence
		if confidence > 0.5:
			# compute the (x, y)-coordinates of the bounding box for
			# the object
			box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
			(startX, startY, endX, endY) = box.astype("int")

			# ensure the bounding boxes fall within the dimensions of
			# the frame
			(startX, startY) = (max(0, startX), max(0, startY))
			(endX, endY) = (min(w - 1, endX), min(h - 1, endY))

			# extract the face ROI, convert it from BGR to RGB channel
			# ordering, resize it to 224x224, and preprocess it
			face = frame[startY:endY, startX:endX]
			face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
			face = cv2.resize(face, (224, 224))
			face = img_to_array(face)
			face = preprocess_input(face)

			# add the face and bounding boxes to their respective
			# lists
			faces.append(face)
			locs.append((startX, startY, endX, endY))

	# only make a predictions if at least one face was detected
	if len(faces) > 0:
		# for faster inference we'll make batch predictions on *all*
		# faces at the same time rather than one-by-one predictions
		# in the above `for` loop
		faces = np.array(faces, dtype="float32")
		preds = maskNet.predict(faces, batch_size=32)
	
	orang = str(len(faces))
	link = "https://risetkanta.com/mask-detection/inputOrg.php?id=1&total="+orang
	#db1 = requests.get(link)
			
	# return a 2-tuple of the face locations and their corresponding
	# locations
	return (locs, preds)

# load our serialized face detector model from disk
prototxtPath = r"face_detector\deploy.prototxt"
weightsPath = r"face_detector\res10_300x300_ssd_iter_140000.caffemodel"
faceNet = cv2.dnn.readNet(prototxtPath, weightsPath)

# load the face mask detector model from disk
maskNet = load_model("mask_detector.model") # tensor flow detect

# initialize the video stream
print("[INFO] starting video stream...")
vs = VideoStream('http://192.168.137.57:8081').start()
#vs = VideoStream(SCR=0).start()
# loop over the frames from the video stream
while True:
	# grab the frame from the threaded video stream and resize it
	# to have a maximum width of 400 pixels
	frame = vs.read()
	frame = imutils.resize(frame, width=400)
	# detect faces in the frame and determine if they are wearing a
	# face mask or not
	(locs, preds) = detect_and_predict_mask(frame, faceNet, maskNet)
	
	# loop over the detected face locations and their corresponding
	# locations
	for (box, pred) in zip(locs, preds):
		# unpack the bounding box and predictions
		(startX, startY, endX, endY) = box
		(mask, withoutMask) = pred
		roi_color = frame[startY:endY, startX:endX]
		# determine the class label and color we'll use to draw
		# the bounding box and text
		label = "Mask" if mask > withoutMask else "No Mask"
		color = (0, 255, 0) if label == "Mask" else (0, 0, 255)

		# include the probability in the label
		label = "{}: {:.2f}%".format(label, max(mask, withoutMask) * 100)

		# display the label and bounding box rectangle on the output
		# frame
		cv2.putText(frame, label, (startX, startY - 10),
			cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)
		cv2.rectangle(frame, (startX, startY), (endX, endY), color, 2)


		if withoutMask > mask:
			img_item = "tersangka.png"
			cv2.imwrite(img_item, roi_color)
			

			if (x == 1):
				print("mengirim")
				send_msg_tsg("The system has detect some offense at the first carriage")
				db =  requests.get('https://risetkanta.com/mask-detection/input.php?status=1')		
				x = 0
				y = 1
				counter2 = 11
				counter3= 5
		if y == 1 :					
				
			if time.time() - start2 > 1:
				start2 = time.time()
				counter2 = counter2 - 1

			if counter2 <= 0 :
				counter2 = 11
				y1 = 0
			
			if y1 == 0 :
				if withoutMask > mask:
					send_msg("the system still detect some offense, if you have finished give punishment please click /finish")
					bot1.polling()
					counter2 = 11
					counter = 0	
					y = 0
					x = 1
					y1 = 1
				else : 
					send_msg("The suspect has already wear a mask")
					counter2 = 11
					counter = 0	
					y = 0
					x = 1
					y1 = 1

	# show the output frame
	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF

	# if the `q` key was pressed, break from the loop
	if key == ord("q"):
		break

# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()