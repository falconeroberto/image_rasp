#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 19:12:01 2020

@author: pi
"""

import paho.mqtt.client as mqtt

# This is the Publisher

client = mqtt.Client()
client.connect("192.168.43.2",1883,60)
client.publish("sensor/data", "Hello world!");
client.disconnect();