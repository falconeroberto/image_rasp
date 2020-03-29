#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 25 16:28:58 2020

@author: pi
"""
from picamera import PiCamera
from time import sleep

camera = PiCamera()
camera.start_preview()
camera.start_recording('/home/pi/video3.h264')
sleep(53)
camera.stop_recording()
camera.stop_preview()