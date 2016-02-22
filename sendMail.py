#!/usr/bin/env python
#coding=utf-8
import subprocess
import os
import base64
import sys
import MySQLdb
from email.mime.text import MIMEText
from pycall import CallFile, Call, Application
from datetime import datetime
import time
from DBCode import DBCode
from netmiko import ConnectHandler
from multiprocessing import Process, Queue, Value, Array
import Queue as CheckQueue
import getopt
import getpass
import subprocess
import smtplib
from decimal import Decimal
import re

"""
 This method used to send mail to given mailID with proper info.
"""
def sendMail(sev,circuitProvider,msg):
                subject  = sev+" Circuit ID :"+circuitProvider
                message = "Team" + "\n" + "\n" + "Please find  details about the devices\n\n" +msg
                smtpserver= "relay.emc-corp.net:25"
                to_addr_list = ["gowdham@timebender.in"]
                from_addr_list = "Network-engineering"

                msg = MIMEText(message)
                msg['Subject'] = subject
                msg['From'] = from_addr_list
                msg['To'] = ", ".join(to_addr_list)

                server = smtplib.SMTP(smtpserver)
                server.ehlo()
                send = server.sendmail(from_addr_list, to_addr_list, msg.as_string())
                server.quit()
"""
This method used to create references to the DBCode class.
"""
def createDBObject():
                try:
                                db = DBCode()
                                return db
                except Exception as e:
                                print "Exception occured during Database Connection",str(e)
"""
 Set timeout variable 
"""
def getTimeout():
                timeout="1"
                return timeout

"""
 Get the current date and time as seconds
"""
def getDateTime():
                dt=datetime.today()
                seconds=time.mktime(dt.timetuple())
                return seconds

"""
  This methos used to fecth the values from CoreRouterState table and check Time field if time value exceeds more than one seconds then it will do ping test and send the mail with proper info based on ping test result.
"""
def checkAfterTimeout(db):
                while 1:
                                try:
                                                record=db.selectTable('CoreCircuitStates')
                                                seconds=getDateTime()
                                                for rec1 in record:
                                                                if str(rec1[4]) == '0':
                                                                                continue
                                                                diff=Decimal(seconds) - Decimal(rec1[4])
                                                                if int(diff) >= 60:
                                                                                setFlag=[]
                                                                                row=db.selectCoreRouterDetails(rec1[0])
                                                                                for rec in row:
                                                                                                result,AEndIntf,BEndIntf,pingA,pingB=pingTest(str(rec[10]),str(rec[11]),str(rec[5]),str(rec[7]))
                                                                                                if result == 0:
                                                                                                                setFlag.append(rec1[0])
                
                                                                                                                setFlag.append('YES')
                
                                                                                                                setFlag.append('0')
                                                                                                                
                                                                                                                setGOCFlag(db,setFlag,str(rec[4]),str(rec[5]),str(rec[6]),str(rec[7]),str(rec[8]),str(rec1[2]),str(rec1[0]),AEndIntf,BEndIntf,pingA,pingB)
                                                                                                else:
                
                                                                                                                setFlag.append(rec1[0])
                                                                                                                
                                                                                                                setFlag.append("0")
                                                                                                                
                                                                                                if "down" in rec1[2]:
                                                                                                
                                                                                                                setFlag.append("UP")
                                                                                                
                                                                                                                db.updateSLAState(setFlag)
                                                                                                
                                                                                                else:
                                                                                                
                                                                                                                db.updateTime(setFlag)
                                                                                                
                
                                except Exception as e:
                                                print "Exception occured ",str(e)
                
                
"""
If ping test fail then it set GOCFlag as yes and send mail to given mail ID with proper info.
"""
def setGOCFlag(db,values,val1,val2,val3,val4,val5,val6,val7,AEndIntf,BEndIntf,pingA,pingB):
                db.updateTable(values)
                msg=""
                sev="Sev2"
                message=""
                circuitProvider=val7
                if "down" in val6:
                                msg="Down"
                else:


                                msg="Packet Loss. Loss Percentage is :"+val6+"%"
                fetchedValues,fetchedValues1,flag=db.getInternalCircuitCountMatch(val7)
                if flag:
                                circuitProvider = ""
                                sev="Sev1"
                                for val in fetchedValues:
                                                slaState=""
                                                for val1 in fetchedValues1:
                                                                if str(val[9]) == str(val1[0]):
                                                                                circuitProvider=circuitProvider+","+str(val1[0])
                                                                                if "down" in str(val1[2]):
                                                                                                slaState="Down"
                                                                                else:
                                                                                                slaState="Packet Loss. Loss Percentage is :"+str(val1[2])+"%"
                                                                                break
           
                                                message=message+"\n AEnd Device :"+str(val[4])+" Interface :"+str(val[5])+"\n ZEnd Device :"+str(val[6])+" Interface :"+str(val[7])+"\n Circuit Provider :"+str(val[8])+"\n SLAStatus :"+slaState+"\n\n"
                else:
                                message="\n AEnd Device :" +val1+"  Interface : "+val2+"\n ZEnd Device :"+val3+"  Interface :"+val4+"\n Circuit Provider :"+val5+"\n SLASTatus :"+msg
                message+="\n\n Ping result from Device " +AEndIntf+" to Device "+BEndIntf+" \n      "+pingA+"\n\n Ping result from Device "+BEndIntf+" to Device "+AEndIntf+" \n       "+pingB+"\n\n"
                sendMail(sev,circuitProvider,message)
                
def pingTest(device1,device2,aIntf,bIntf):
                                try:
                                                                username="cisco"
                                                                password="cisco"
                                                                timeout=getTimeout()
                                                                AEnddevice = ConnectHandler(device_type="cisco_ios", ip=device1, username=username, password=password)
                                                                command='sh run interface '+aIntf
                                                                output1 = AEnddevice.send_command(command)
                                                                output1 = str(output1)
                                                                match=re.match(r'.*ip\s+address\s+(.*)\s+255.*',output1,re.DOTALL)
                                                                if match:
                                                                                AEndIntf=match.group(1)
                                
                                                                BEnddevice = ConnectHandler(device_type="cisco_ios", ip=device2, username=username, password=password)
                                                                command='sh run interface '+bIntf
                                                                output1 = BEnddevice.send_command(command)
                                                                output1 = str(output1)
                                                                match=re.match(r'.*ip\s+address\s+(.*)\s+255.*',output1,re.DOTALL)
                                                                if match:
                                                                                                BEndIntf=match.group(1)
                                
                                                                command='ping '+BEndIntf.strip()+' source '+AEndIntf.strip()+' repeat 30 timeout '+timeout
                                                                output1 = AEnddevice.send_command(command)
                                                                output1 = str(output1)
                                                                pingA = output1
                                                                match=re.match(r'.*rate\s+is\s+(.*)\s+percent.*',output1,re.DOTALL)
                                                                if match:
  
                                                                                pingResultB=match.group(1)
                                                                if pingResultA.strip() > 99 and  pingResultB.strip() > 99:
                                                                                return 1,AEndIntf,BEndIntf,pingA,pingB
                                                                else:
                                                                                return 0,AEndIntf,BEndIntf,pingA,pingB
                                except Exception as e:
                                                print "Error occured while executing commands on Routers"+str(e)
                                                
                                                                                                
if __name__=="__main__":
                db=createDBObject()
                checkAfterTimeout(db)


                                                
