#!/usr/bin/env python
import subprocess
import os
import smtplib
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
import re
"""
 To sendmail if any error in Orion Machine
"""
def sendMail(messagelog):
                subject  = "Syslog correlator Exception!!"
                message = "Team" + "\n" + "\n" + "Please investigate this Exception\n\n" + "\n" + messagelog

                smtpserver= "relay.emc-corp.net:25"
                to_addr_list = ["sretnamony@emc-corp.net"]
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
  To fetch data from table and check the message which has orion alert in it.If so then check message has down or packet loss string.
"""
def OrionAlerts(db):
                
                                from datetime import date
                
                                #Initialize Orion-KPI-ALert to False
                                ORION_Core_KPI_Alert = False
                
                                #EDIT THIS PARAMETERS WITH YOUR DATABASE INFORMATION
                                HOST = "localhost"
                                USER = "root"
                                PSWD = base64.b64decode("RGU3bGMzLVMhIQ==")
                                DBNM = "syslogng"
                
                                #CONNECTING TO DATABASE
                                db = MySQLdb.connect(
                        host  = HOST,
                        user  = USER,
                        passwd= PSWD,
                        db    = DBNM
                                )
                                cur = db.cursor()
                
                                #CREATE TABLE NAME
                                year  = str(date.today().year)
                                month = date.today().month
                                if month <= 9:
                                                                month = "0"+str(month)
                                else:
                                                                month = str(month)
                                table = "syslog_" + year + month
                                                
                                #LOOK FOR NEW RECORDS ON DB
                                cur.execute("SELECT * FROM "+table)
                                for row in cur.fetchall() :
                                                
                                                                host    = row[4]
                                                                message = row[7]
                                                                flag    = row[1]
                                                
                                                                #IF MESSAGE AND HOST HAVE THE CORRECT STRINGS
                                                                if "orion" in host:
                                                                                                if "Core-KPI-Alert" in message:
                                                                                                #IF IS A NEW MESSAGE (CHECKING FLAG COLUMN)
                                                                                                                                if flag == "0":
                                                                                                                                                                ORION_Core_KPI_Alert = True
                                                                                                                                                                cur.execute("UPDATE "+table+" SET flag='1' WHERE seq="+str(row[0]))
                                                                                                                                                                parseMessage(message,db)
                                                
                                                
                                if ORION_Core_KPI_Alert == True:
                                                                return "ORION-Core-KPI-Alert"
                                

"""
 To create refernces for DBCode class 
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
                                timeout='1'
                                return timeout

"""
 Set lossPercent variable
"""
def losspercent():
                                lossPercent=50
                                return lossPercent

"""
 Get the current date and time as seconds
"""
def getDateTime():
                                dt=datetime.today()
                                seconds=time.mktime(dt.timetuple())
                                return seconds

"""
 Update Time in corerouterstate table
"""
def callDBtoUpdateTime(values,db):
                                try:
                                                                db.updateTime(values)
                                except Exception as e:
                                                                print "Exception occured while updating Database table",str(e)   
"""
  Parse the message and do the action based on that
"""
def parseMessage(message,db):
                                msg=""
                                lossPercentage=""
                                if "down" in message:
                                                                match=re.match(r'.*-\s+(.*)\s+is.*',message,re.M|re.I)
                                                                if match:
                                                                                                patternTag=match.group(1)
                                                                                                msg="down"
                                elif "loss" in message:
                                                                match=re.match(r'.*-\s+(.*)\s+has\s*(.*)\s+packet.*',message,re.M|re.I)
                                                                if match:
                                                                                                patternTag=match.group(1)
                                                                                                lossPercentage=match.group(2)
                                                                                                msg="loss"
                                                                                                if lossPercentage < losspercent():
                                                                                                                                return
                
                                selectRecord(patternTag.strip(),db,msg,lossPercentage)
                                
"""
 Fetch device details from CoreRouter table and check devices are up or not.
"""
def selectRecord(value,db,msg,lossPercentage):
                                try:
                                                                record=db.selectRecord(value)
                                                                result = -1
                                                                for rec in record:
                                                                                                result=pingTest(str(rec[10]),str(rec[11]),str(rec[5]),str(rec[7]))
                                                                                                if result == 0:
                                                                                                                                value=[]
                                                                                                                                value.append(rec[9])
                                                                                                                                if "down" in msg:
                                                                                                                                                                value.append('LINK')
                                                                                                                                                                value.append('DOWN')
                                                                                                                                                                value.append('NO')
                                                                                                                                else:
                                                                                                                                                                value.append('Packet Loss')
                                                                                                                                                                value.append(lossPercentage)
                                                                                                                                                                value.append('NO')
                                                                                                                                value.append('0')
                                                                                                                                try:
                                                                                                                                                                db.insertValuesIntoCoreRouterStateTable(value)
                                                                                                                                except Exception as e:
                                                                                                                                                                pass
                                                                                                                                seconds=getDateTime()
                                                                                                                                temp = []
                                                                                                                                temp.append(str(rec[9]))
                                                                                                                                temp.append(seconds)
                                                                                                                                callDBtoUpdateTime(temp,db)
                                except Exception as e:
                                                                print "Exception occured while fetching records",str(e)
                                    
"""
   Check ping test from both ends and update the table with proper info
"""
def pingTest(device1,device2,aIntf,bIntf):
                                try:
                                                                username='cisco'
                                                                password='cisco'
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
                                                                output2 = BEnddevice.send_command(command)
                                                                output2 = str(output2)
                                                                match=re.match(r'.*ip\s+address\s+(.*)\s+255.*',output2,re.DOTALL)
                                                                if match:
                                                                                                BEndIntf=match.group(1)
                                                                                               
                                
                                                                command='ping '+BEndIntf.strip()+' source '+AEndIntf.strip()+' repeat 30 timeout '+timeout
                                                                output1 = AEnddevice.send_command(command)
                                                                output1=str(output1)
                                                                match=re.match(r'.*rate\s+is\s+(.*)\s+percent.*',output1,re.DOTALL)
                                                                if match:
                                                                                                pingResultA=match.group(1)
                                                                    
                                                                command='ping '+AEndIntf.strip()+' source '+BEndIntf.strip()+' repeat 30 timeout '+timeout
                                                                output1 = BEnddevice.send_command(command)
                                                                output1 = str(output1)
                                                                match=re.match(r'.*rate\s+is\s+(.*)\s+percent.*',output1,re.DOTALL)
                                                                if match:
                                                                                                pingResultB=match.group(1)
                                                                                               
                                                                if pingResultA.strip() > 99 and  pingResultB.strip() > 99:
                                                                                                return 1
                                                                else:
                                                                                                return 0
                                except Exception as e:
                                                                print "Error occured while executing commands on Routers"+str(e)


def PyCall():
                                    
                                    #This module calls EMC GOC hunt group number "1180"
                                    
                                callpbx = Call('SIP/emcpbx/1180', callerid = "'Syslog-Correlator' <0210>")
                                callpbxapp = Application('Playback', 'CORE-ORION-ALERTgsm')
                                cf = CallFile(callpbx, callpbxapp)
                                cf.spool()
                                
                                    
def PreviousTime():
                                    
                                    #This module accesses the database for previous time and return the previous time as datetime object
                                    
                                import datetime
                                #EDIT THIS PARAMETERS WITH YOUR DATABASE INFORMATION
                                HOST = "localhost"
                                USER = "root"
                                PSWD = base64.b64decode("RGU3bGMzLVMhIQ==")
                                DBNM = "syslogng"
                
                                #CONNECTING TO DATABASE
                                db = MySQLdb.connect(
                                     host  = HOST,
                                     user  = USER,
                                     passwd= PSWD,
                                     db    = DBNM
                                    )
                                cur = db.cursor()
                                    
                                #LOOK FOR NEW RECORDS ON DB
                                cur.execute("SELECT * FROM status_time")
                                for row in cur.fetchall() :
                                                                year    = row[1]
                                                                month   = row[2]
                                                                day     = row[3]
                                                                hour    = row[4]
                                                                minute  = row[5]
                                                                second  = row[6]
                                                                microsecond = row[7]
                                                            
                                return datetime.datetime (int(year),int (month),int (day), int (hour), int (minute), int (second), int (microsecond))

                                                            
def UpdateTime():
                                                            
                                                            #This module accesses the database to store the current time in memory
                                                                import datetime
                                                
                                                                t1 = datetime.datetime.now()
                                                
                                                                year    = str(t1.year)
                                                                month   = str(t1.month)
                                                                day     = str(t1.day)
                                                                hour    = str(t1.hour)
                                                                minute  = str(t1.minute)
                                                                second  = str(t1.second)
                                                                microsecond = str(t1.microsecond)
                                                
                                                                #EDIT THIS PARAMETERS WITH YOUR DATABASE INFORMATION
                                                                HOST = "localhost"
                                                                USER = "root"
                                                                PSWD = base64.b64decode("RGU3bGMzLVMhIQ==")
                                                                DBNM = "syslogng"
                                                                
                                                                #CONNECTING TO DATABASE
                                                                db = MySQLdb.connect(
                                                                        host  = HOST,
                                                                        user  = USER,
                                                                        passwd= PSWD,
                                                                        db    = DBNM
                                                                                )
                                                                cur = db.cursor()
                                                                            
                                                                cur.execute("UPDATE status_time SET year="+year)
                                                                cur.execute("UPDATE status_time SET month="+month)
                                                                cur.execute("UPDATE status_time SET day="+day)
                                                                cur.execute("UPDATE status_time SET hour="+hour)
                                                                cur.execute("UPDATE status_time SET minute="+minute)
                                                                cur.execute("UPDATE status_time SET second="+second)
                                                                cur.execute("UPDATE status_time SET microsecond="+microsecond)
                                                                
def TimeElapsed():
                                                                                            
                                                                #This module accesses the database for previous time call was lodged to GOC and calculated the time difference in minutes
                                                                import datetime
                                                                t1 = PreviousTime()
                                                                t2 = datetime.datetime.now()
                                                                td = t2 - t1
                                                                return (td.days*1440)+ (td.seconds/60) + ((td.microseconds/1000/1000)/60)
                                
                                                                                            
def CallGOC():
                                                                                            
                                #This module accesses the database "syslogng" and table "status_time" to check whether EMC GOC can be called to inform about this Alert
                                import datetime
                                #EDIT THIS PARAMETERS WITH YOUR DATABASE INFORMATION
                                HOST = "localhost"
                                USER = "root"
                                PSWD = base64.b64decode("RGU3bGMzLVMhIQ==")
                                DBNM = "syslogng"
                
                                #CONNECTING TO DATABASE
                                db = MySQLdb.connect(
                        host  = HOST,
                        user  = USER,
                        passwd= PSWD,
                        db    = DBNM
                                )
                                cur = db.cursor()
                                                                                                            
                                #LOOK whether the pycall action is enabled
                                                                                                            
                                cur.execute("SELECT enable FROM status_time")
                                                                                                            
                                for row in cur.fetchall() :
                                                                CallGOCstatus = row[0]
                
                                if (CallGOCstatus == "1"):
                                                                return True
                                else:
                                                                return False
                                                                                                            
                                                                                                            
def main():
                                                                try:
                                                                                                                           
                                                                                                db=createDBObject()
                                                                                                #message="1/7/2016 3:10 AM: Core-KPI-Alert - RAI_LND_1Gig_T-SYSTEM_0EV/4_Diessen is down"   
                                                                                               # message="1/12/2016 4:08 PM: Core-KPI-Alert - RAI_LND_1Gig_T-SYSTEM_0EV/3_Diessen has 98.4000015258789 packet loss"
                                                                                                #parseMessage(message,db)
                                                                                                Alertmessage = OrionAlerts(db)
                                                                                                                            
                                                                                                if Alertmessage == "ORION-Core-KPI-Alert":
                                                                                                                                if (TimeElapsed() > 15) and (CallGOC()):
                                                                                                                                                                PyCall()
                                                                                                                                                                UpdateTime()
                                                                                
                                                                                                                            
                                                                except Exception, err:
                                                                                                sendMail("ERROR: %s\n" % str(err))
                                                                                                                            
                                                                                                                            
if __name__ == '__main__':
                                main()

                                                                                                                            
                                                                                                    
