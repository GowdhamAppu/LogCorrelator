#! /usr/bin/env python

#*--------------------------------------------------------------
#* common.py
#*
#*--------------------------------------------------------------
#*@author:Gowdhaman Mohan
import os.path
import sys
file_path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.path.pardir))
if file_path not in sys.path:
    sys.path.insert(0, file_path)
class common: 
        @staticmethod
        def getTimeZoneDifferent(): 
            timeZoneDifferent = 1
            return timeZoneDifferent
   
        @staticmethod
        def getEmailList(severity):
            if severity.strip() == "sev1":
                emailList = ["pvijay@emc-corp.net","Gowdhaman.Mohan@emcconnected.com"]
            else:
                emailList = ["Gowdhaman.Mohan@emcconnected.com","gowdham@timebender.in"]  
            return emailList
   
        @staticmethod
        def getScanInterval():
                scanInterval = 1  
                return scanInterval
     
        @staticmethod
        def getRouterCredentials():
            username = "pavijay"
            password = "WAnoharan!123"
            return username,password

