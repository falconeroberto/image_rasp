#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 28 20:53:12 2020

@author: pi
"""

#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 28 20:47:13 2020

@author: pi
"""

#!/usr/bin/env python2
# -*- coding: utf-8 -*-
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
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['MQTT_BROKER_URL'] = '192.168.43.3  # use the free broker from HIVEMQ
app.config['MQTT_BROKER_PORT'] = 1883  # default port for non-tls connection
#app.config['MQTT_USERNAME'] = ''  # set the username here if you need authentication for the broker
#app.config['MQTT_PASSWORD'] = ''  # set the password here if the broker demands authentication
app.config['MQTT_KEEPALIVE'] = 5  # set the time interval for sending a ping to the broker to 5 seconds
app.config['MQTT_TLS_ENABLED'] = False  # set TLS to disabled for testing purposes
app.config['MQTT_CLEAN_SESSION'] = True

mqtt = Mqtt(app)
socketio = SocketIO(app)
bootstrap = Bootstrap(app)
sub_topic = "alarm"    # receive messages on this topic
sub_topic_act= "active"
port = 5000
alarm= False
active= False

@socketio.on('publish')
def handle_publish(json_str):
    data = json.loads(json_str)
    mqtt.publish(data['topic'], data['message'])


@socketio.on('subscribe')
def handle_subscribe(json_str):
    data = json.loads(json_str)
    mqtt.subscribe(data['topic'])


@socketio.on('unsubscribe_all')
def handle_unsubscribe_all():
    mqtt.unsubscribe_all()


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
 
def gen(camera):
    print(":gen camera")
    while True:
        frame = camera.get_frame()
        if frame:
         print("frame generated")
         yield (b'--frame\r\n'
         b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        else:
         print("frame not generated")
        sleep(5)
        
@app.route('/video_feed')
def video_feed():
    print(":video_feed")
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')    

if __name__ == '__main__':
    socketio.run(app, host='localhost', port=5000, use_reloader=False, debug=False)