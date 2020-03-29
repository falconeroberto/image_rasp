#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 29 19:24:20 2020

@author: pi
"""
#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 29 03:42:29 2020

@author: pi
"""
# import the necessary packages
from imutils import build_montages
from datetime import datetime
import numpy as np
from imagezmq import imagezmq
import argparse
import imutils
import cv2
import eventlet
import json
from flask import Flask, render_template,Response
from flask_mqtt import Mqtt
from flask_socketio import SocketIO
from flask_bootstrap import Bootstrap
from camera2 import VideoCamera
from time import sleep


eventlet.monkey_patch()
app = Flask(__name__)
# if current time *minus* last time when the active device check
# was made is greater than the threshold set then do a check
app.config['TEMPLATES_AUTO_RELOAD'] = True
#app.config['MQTT_BROKER_URL'] = '192.168.43.3'
## use the free broker from HIVEMQ
#app.config['MQTT_BROKER_PORT'] = 1883  # default port for non-tls connection
##app.config['MQTT_USERNAME'] = ''  # set the username here if you need authentication for the broker
##app.config['MQTT_PASSWORD'] = ''  # set the password here if the broker demands authentication
#app.config['MQTT_KEEPALIVE'] = 5  # set the time interval for sending a ping to the broker to 5 seconds
#app.config['MQTT_TLS_ENABLED'] = False  # set TLS to disabled for testing purposes
#app.config['MQTT_CLEAN_SESSION'] = True

mqtt = Mqtt(app)
socketio = SocketIO(app)
bootstrap = Bootstrap(app)
# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--prototxt", required=True,
    help="path to Caffe 'deploy' prototxt file")
ap.add_argument("-m", "--model", required=True,
    help="path to Caffe pre-trained model")
ap.add_argument("-c", "--confidence", type=float, default=0.2,
    help="minimum probability to filter weak detections")
ap.add_argument("-mW", "--montageW", required=True, type=int,
    help="montage frame width")
ap.add_argument("-mH", "--montageH", required=True, type=int,
    help="montage frame height")
args = vars(ap.parse_args())
# initialize the ImageHub object
imageHub = imagezmq.ImageHub()
# initialize the list of class labels MobileNet SSD was trained to
# detect, then generate a set of bounding box colors for each class
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
    "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
    "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
    "sofa", "train", "tvmonitor"]
# load our serialized model from disk
print("[INFO] loading model...")
#net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])
# initialize the consider set (class labels we care about and want
# to count), the object count dictionary, and the frame  dictionary
CONSIDER = set(["dog", "person", "car"])
objCount = {obj: 0 for obj in CONSIDER}
frameDict = {}
# initialize the dictionary which will contain  information regarding
# when a device was last active, then store the last time the check
# was made was now
lastActive = {}
lastActiveCheck = datetime.now()
# stores the estimated number of Pis, active checking period, and
# calculates the duration seconds to wait before making a check to
# see if a device was active
ESTIMATED_NUM_PIS = 4
ACTIVE_CHECK_PERIOD = 10
ACTIVE_CHECK_SECONDS = ESTIMATED_NUM_PIS * ACTIVE_CHECK_PERIOD
# assign montage width and height so we can view all incoming frames
# in a single "dashboard"
mW = args["montageW"]
mH = args["montageH"]
print("[INFO] detecting: {}...".format(", ".join(obj for obj in
    CONSIDER)))

sub_topic = "alarm"    # receive messages on this topic
sub_topic_act= "active"
port = 5000
alarm= False
active= False

#@socketio.on('publish')
#def handle_publish(json_str):
#    data = json.loads(json_str)
#    #mqtt.publish(data['topic'], data['message'])
#
#
@socketio.on('subscribe')
def handle_subscribe(json_str):
    data = json.loads(json_str)
    mqtt.subscribe(data['topic'])
#
#
#@socketio.on('unsubscribe_all')
#def handle_unsubscribe_all():
#     # mqtt.unsubscribe_all()
#     return
#
#
@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    data = dict(
        topic=message.topic,
        payload=message.payload.decode()
    )
    global alarm
    global active
    if alarm == True:
     print("flag alarm is:" + str(alarm))
    else:
     print("else flag alarm is:" + str(alarm))

    if active and message.payload == 'alarmed':
     print("received alarmed set flag alarm equal true" + str(message.payload))
     alarm = True
    else:
     if active and message.payload == 'dealarmed':
      print("received dealarmed set flag alarm equal false" + str(message.payload))
      alarm = False
    socketio.emit('mqtt_message', data=data)
#
#
@mqtt.on_log()
def handle_logging(client, userdata, level, buf):
    print(level, buf)

@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    mqtt.subscribe(sub_topic)
    print(":subscribe  " + str(sub_topic))


@app.route('/')
def hello_world():
     global alarm
     global active
     buttonSts= alarm
     senPIRSts = active
     templateData = {
             'button' : buttonSts,
               'senPIR'  : senPIRSts
      }
     return render_template('index.html',**templateData)

@app.route("/<deviceName>/<action>")
def action(deviceName, action):
     global active
     global alarm

     if action == "on" :
        print(":active  action on  " + str(action))
        active = True
        
     if action == "off" :
        print(":active  action off  " + str(action))
        active = False
        
     senPIRSts = active
     buttonSts = alarm
     templateData = {
        'button'  : buttonSts,
        'senPIR': senPIRSts
        }
     return render_template('index.html',**templateData)
 
def gen():
  print(":gen camera")
    # start looping over all the frames
  while True:
    # receive RPi name and frame from the RPi and acknowledge
    # the receipt
    (rpiName, frame) = imageHub.recv_image()
    imageHub.send_reply(b'OK')
    # if a device is not in the last active dictionary then it means
    # that its a newly connected device
    if rpiName not in lastActive.keys():
        print("[INFO] receiving data from {}...".format(rpiName))
    # record the last active time for the device from which we just
    # received a frame
    lastActive[rpiName] = datetime.now()
    # resize the frame to have a maximum width of 400 pixels, then
    # grab the frame dimensions and construct a blob
    frame = imutils.resize(frame, width=400)
    (h, w) = frame.shape[:2]
#    blob=cv2.dnn.blobFromImage(cv2.resize(frame,(300,300)),0.007843,(300,300),127.5)
     
     #predictions
    #net.setInput(blob)
    #detections = net.forward()
     # reset the object count for each object in the CONSIDER set
#    objCount = {obj: 0 for obj in CONSIDER}

     # loop over the detections
#    for i in np.arange(0, detections.shape[2]):
#        # extract the confidence (i.e., probability) associated with
#        # the prediction
#        confidence = detections[0, 0, i, 2]
#        # filter out weak detections by ensuring the confidence is
#        # greater than the minimum confidence
#        if confidence > args["confidence"]:
#            # extract the index of the class label from the
#            # detections
#            idx = int(detections[0, 0, i, 1])
#            # check to see if the predicted class is in the set of
#            # classes that need to be considered
#            if CLASSES[idx] in CONSIDER:
#                # increment the count of the particular object
#                # detected in the frame
#                objCount[CLASSES[idx]] += 1
#                # compute the (x, y)-coordinates of the bounding box
#                # for the object
#                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
#                (startX, startY, endX, endY) = box.astype("int")
#                # draw the bounding box around the detected object on
#                # the frame
#                cv2.rectangle(frame, (startX, startY), (endX, endY),
#                    (255, 0, 0), 2)
#

          #    draw the sending device name on the frame
    cv2.putText(frame, rpiName, (10, 25),
    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    # draw the object count on the frame
#    label = ", ".join("{}: {}".format(obj, count) for (obj, count) in
#    objCount.items())
#    cv2.putText(frame, label, (10, h - 20),
#    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255,0), 2)
    # update the new frame in the frame dictionary
    frameDict[rpiName] = frame
    # buld a montage using images in the frame dictionary
    montages = build_montages(frameDict.values(), (w, h), (mW, mH))
     # display the montage(s) on the screen
    for (i, montage) in enumerate(montages):
#       cv2.imshow("Home pet location monitor ({})".format(i),
#       montage)
#       if montage.any() :
#        print("frame not generated")
       ret, jpeg = cv2.imencode('.jpg', montage)
       yield (b'--frame\r\n'
         b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
       
       sleep(0.1)

#       else:
#         print("frame not generated")
    #sleep(5)
    # detect any kepresses
#    key = cv2.waitKey(1) & 0xFF
#    if (datetime.now() - lastActiveCheck).seconds > ACTIVE_CHECK_SECONDS:
#        # loop over all previously active devices
#       for (rpiName, ts) in list(lastActive.items()):
#       #    remove the RPi from the last active and frame
#       # dictionaries if the device hasn't been active recently
#          if (datetime.now() - ts).seconds > ACTIVE_CHECK_SECONDS:
#            print("[INFO] lost connection to {}".format(rpiName))
#            lastActive.pop(rpiName)
#            frameDict.pop(rpiName)
#     # set the last active check time as current time
#    lastActiveCheck = datetime.now()
       # if the `q` key was pressed, break from the loop
#    if key == ord("q"):
#        break
#        
@app.route('/video_feed')
def video_feed():
    print(":video_feed")
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')    

if __name__ == '__main__':
    print(":gen camera")
    socketio.run(app, host='localhost', port=5000, use_reloader=False, debug=False)
