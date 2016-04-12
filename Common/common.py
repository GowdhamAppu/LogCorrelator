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
        nodeName={}
        @staticmethod
        def getTimeZoneDifferent(): 
            timeZoneDifferent = 1
            return timeZoneDifferent
   
        @staticmethod
        def getEmailList(severity):
            if severity.strip() == "sev1":
                emailList = ["shadrach.retnamony@emcconnected.com","pvijay@emc-corp.net","Gowdhaman.Mohan@emcconnected.com","important-core-notifications@mtnsat.pagerduty.com"]
            elif severity.strip() == "sev2":
                emailList = ["shadrach.retnamony@emcconnected.com","critical-core-notifications@mtnsat.pagerduty.com","Gowdhaman.Mohan@emcconnected.com","pvijay@emc-corp.net"]  
            else:
                emailList = ["pvijay@emc-corp.net","Gowdhaman.Mohan@emcconnected.com"] 
            return emailList
   
        @staticmethod
        def getScanInterval():
                scanInterval = 1  
                return scanInterval
        
        @staticmethod
        def getSendCommandDelayFactor():
            delayFactor = 1
            loop = 40
            return delayFactor,loop
        
        @staticmethod
        def getNodeLossValue():
            lossValue=50
            return lossValue
        
        @staticmethod
        def getNodeName():
            return common.nodeName
        
        @staticmethod
        def setNodeName(key,value):
            common.nodeName[key]=value
            
        @staticmethod
        def checkKeyExists(dictVariable,key):
            if key in dictVariable.keys():
                return True
            else:
                return False
            
        @staticmethod
        def removeKey(key):
            try:
                del common.nodeName[key]
            except Exception as e:
                pass
            
        @staticmethod
        def getNodeCheckInterval():
            interval = 8
            return interval
        
        @staticmethod
        def getRouterCredentials():
            username = "pavijay"
            password = "WAnoharan!123"
            return username,password
        
        @staticmethod
        def getAdditionalMailID():
            mailID="paul.vijay@emcconnected.com,Gowdaman.Mohan@emcconnected.com"
            return mailID




