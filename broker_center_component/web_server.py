"""
Created on Tue Mar 24 00:44:22 2020

@author: pi
"""

from flask import Flask
import paho.mqtt.client as mqtt
import eventlet
from flask_mqtt import Mqtt
from flask import Flask, render_template
from flask_socketio import SocketIO
from flask_bootstrap import Bootstrap

eventlet.monkey_patch()
app = Flask(__name__)
app.config['MQTT_BROKER_URL'] = '192.168.43.4'  # use the free broker from HIVEMQ
app.config['MQTT_BROKER_PORT'] = 1883  # default port for non-tls connection
#app.config['MQTT_USERNAME'] = ''  # set the username here if you need authentication for the broker
#app.config['MQTT_PASSWORD'] = ''  # set the password here if the broker demands authentication
app.config['MQTT_KEEPALIVE'] = 5  # set the time interval for sending a ping to the broker to 5 seconds
app.config['MQTT_TLS_ENABLED'] = False  # set TLS to disabled for testing purposes
mqtt = Mqtt(app)
socketio = SocketIO(app)
bootstrap = Bootstrap(app)
sub_topic = "alarm"    # receive messages on this topic
sub_topic_act= "active"
port = 5000
alarm=False
#
#@app.route('/')
#def index():
#    return 'hello'


@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    mqtt.subscribe(sub_topic)
    print(":subscribe  " + str(sub_topic))


@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    print(":pub  on message received"+"MESSAGE: "+message)
#    if message.payload=="alarmed" :
#     print("alarmed signale arrived in messages turn vaariable")
#     alarm=True

@app.route('/')
def hello_world():
#    buttonSts = alarm
#    templateData = {'button':buttonSts}
     return render_temp('index.html')#,**templateData)

if __name__ == '__main__':
#    client = mqtt.Client()
#    #client.username_pw_set(username, password)
#    client.on_connect = on_connect
#    client.on_message = on_message
#    client.connect("192.168.43.2",1883, 60)
#    client.loop_start()
#    important: Do not use reloader because this will create two Flask instances.
#    Flask-MQTT only supports running with one instance
    socketio.run(app, host='0.0.0.0', port=5000, use_reloader=False, debug=False)