#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 25 17:10:17 2020

@author: pi
"""
import cv2

class VideoCamera(object):
    def __init__(self):
        # Using OpenCV to capture from device 0. If you have trouble capturing
        # from a webcam, comment the line below out and use a video file
        # instead.
        self.video = cv2.VideoCapture(-1)
        # Check if camera opened successfully
        if (self.video.isOpened() == False): 
         print("Unable to read camera feed init")
        # If you decide to use video.mp4, you must have this file in the folder
        # as the main.py.
        #self.video = cv2.VideoCapture('/home/pi/video3.h264')
    
    def __del__(self):
        self.video.release()
    
    def get_frame(self):
        cv2.namedWindow("preview")

        if self.video.isOpened(): # try to get the first frame
         rval, frame = self.video.read()
        else:
         rval = False

        while rval:
         cv2.imshow("preview", frame)
         rval, frame = self.video.read()
         key = cv2.waitKey(20)
         if key == 27: # exit on ESC
          break
        cv2.destroyWindow("preview")
        
        if (self.video.isOpened() == False): 
         print("Unable to read camera feed after")
        else:
         success, image = self.video.read()
         # We are using Motion JPEG, but OpenCV defaults to capture raw images,
         # so we must encode it into JPEG in order to correctly display the
         # video stream
         if success:
          ret, jpeg = cv2.imencode('.jpg', image)
          return jpeg.tobytes()
     