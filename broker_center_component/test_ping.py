#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 28 20:56:41 2020

@author: pi
"""

import os
hostname = "google.com" #example
response = os.system("ping -c 1 " + hostname)

#and then check the response...
if response == 0:
  print hostname, 'is up!'
else:
  print hostname, 'is down!'