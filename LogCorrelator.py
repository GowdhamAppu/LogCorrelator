#!/usr/bin/env python
import subprocess
from decimal import Decimal
import os
import os.path
import smtplib
import base64
import sys
import MySQLdb
import sys
file_path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.path.pardir))
if file_path not in sys.path:
    sys.path.insert(0, file_path)
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
from common import common
from log import log


def sendAuthFailMail(device1,device2):
                subject = "Authentication  failed on routers "+device1+","+device2
                log.warning("Access to router got Failed so sent mail to given mail List that Authentication failed on routers %s , %s ",str(device1),str(device2))
                smtpserver="relay.emc-corp.net:25"
                to_addr_list = common.getEmailList('exception')
                #to_addr_list = ["Gowdhaman.Mohan@emcconnected.com","pvijay@emc-corp.net"]
                from_addr_list = "Network-engineering"
                messages="Error Occured During Router Login.Authentication Failed."
                msg = MIMEText(messages)
                msg['Subject'] = subject
                msg['From'] = from_addr_list
                msg['To'] = to_addr_list
                server = smtplib.SMTP(smtpserver)
                server.ehlo()
                send = server.sendmail(from_addr_list,to_addr_list,msg.as_string())
                server.quit()

"""
 To sendmail if any error in Orion Machine
"""
def sendMail(messagelog):
                subject  = "Syslog correlator Exception!!"
                message = "Team" + "\n" + "\n" + "Please investigate this Exception\n\n" + "\n" + messagelog
                log.info("Syslog correlator Exception %s",str(messagelog))
                smtpserver= "relay.emc-corp.net:25"
                to_addr_list = common.getEmailList('exception')
                #to_addr_list = ["Gowdhaman.Mohan@emcconnected.com","pvijay@emc-corp.net"]
                from_addr_list = "Network-engineering"

                msg = MIMEText(message)
                msg['Subject'] = subject
                msg['From'] = from_addr_list
                msg['To'] = to_addr_list

                server = smtplib.SMTP(smtpserver)
                server.ehlo()
                send = server.sendmail(from_addr_list, to_addr_list, msg.as_string())
                server.quit()

"""
  To fetch data from table and check the message which has orion alert in it.If so then check message has down or packet loss string.
"""
def OrionAlerts():
                
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
                                #log.info("Fetch recotrds from table %s",str(table))                
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
                                                                                                                                                                log.info("Got Alert from OrionServer %s",str(message))
                                                                                                                                                                ORION_Core_KPI_Alert = True
                                                                                                                                                                cur.execute("UPDATE "+table+" SET flag='1' WHERE seq="+str(row[0]))
                                                                                                                                                                #parseMessage(message,db)
                                                
                                                
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
                                                                log.warning("Exception occured during Database Connection %s",str(e))

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
                                                                log.warning("Exception occured while updating values in CoreCircuitStates Database table %s",str(e))   
"""
  Parse the message and do the action based on that
"""
def parseMessage(message,db):
                                msg=""
                                lossPercentage=""
                                latencyValue="NO"
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
                                elif "Latency" in message:
                                                                match=re.match(r'.*-\s+(.*)\s*-.*is\s*(\d+).*',message,re.M|re.I)
                                                                if match:
                                                                                                patternTag=match.group(1)
                                                                                                latencyValue=match.group(2)
                                                                                                msg="latency"                                                                   
                                try:     
                                    selectRecord(patternTag.strip(),db,msg,lossPercentage)
                                except Exception as e:
                                    return                   
                                
"""
 Fetch device details from CoreRouter table and check devices are up or not.
"""
def selectRecord(value,db,msg,lossPercentage):
                                try:
                                                                #print value
                                                                log.info("Parsed pattern Tag %s",str(value))
                                                                record=db.selectRecord(value)
                                                                log.info("Fecthed records %s",str(record))
                                                                result = -1
                                                                for rec in record:
                                                                                                log.info("Check InternalCircuitID (%s) is present in CoreCircuitStates table or not.",str(rec[9]))
                                                                                                check=db.checkInTable(str(rec[9]))
                                                                                                if int(check) == 1:
                                                                                                        log.info('Present in CoreCircuitStates table.so move to next record') 
                                                                                                        continue  
                                                                                                log.info('InternalCircuitID is not present in the CoreCircuitStates table.so going to perform pingtest on both end of the devices.')    
                                                                                                result,devicelatency,deviceSecLatency=pingTest(str(rec[10]),str(rec[11]),str(rec[5]),str(rec[7]),msg,str(rec[12]))
                                                                                                
                                                                                                if result == 0:
                                                                                                                                value=[]
                                                                                                                                value.append(rec[9])
                                                                                                                                if "down" in msg:
                                                                                                                                                                value.append('LINK')
                                                                                                                                                                value.append('DOWN')
                                                                                                                                                                value.append('NO')
                                                                                                                                elif "loss" in msg:
                                                                                                                                                                value.append('Packet Loss')
                                                                                                                                                                value.append(lossPercentage)
                                                                                                                                                                value.append('NO')
                                                                                                                                                                  
                                                                                                                                else:
                                                                                                                                                                value.append('Latency')
                                                                                                                                                                if devicelatency == 0 or deviceSecLatency == 0:
                                                                                                                                                                    value.append('Latency Less')
                                                                                                                                                                else:
                                                                                                                                                                    value.append('No Latency')
                                                                                                                                                                value.append('NO')
                                                                                                                                value.append('0')
                                                                                                                                try:
                                                                                                                                                                
                                                                                                                                                                db.insertValuesIntoCoreRouterStateTable(value)
                                                                                                                                                                log.info("Record(%s) inserted into CoreCircuitStates table ",str(value))
                                                                                                                                except Exception as e:
                                                                                                                                                                pass
                                                                                                                                seconds=getDateTime()
                                                                                                                                temp = []
                                                                                                                                temp.append(str(rec[9]))
                                                                                                                                temp.append(seconds)
                                                                                                                                callDBtoUpdateTime(temp,db)
                                except Exception as e:
                                                                log.info("Exception occured while fetching records %s",str(e))
                                    
"""
   Check ping test from both ends and update the table with proper info
"""
def pingTest(device1,device2,aIntf,bIntf,latency,latencyValue):
                                try:
                                                                username,password=common.getRouterCredentials()
                                                                #password='WAnoharan!123'
                                                                delayFactor,loop = common.getSendCommandDelayFactor()
                                                                timeout=getTimeout()
                                                                AEnddevice = ConnectHandler(device_type="cisco_ios", ip=device1, username=username, password=password)
                                                                command='sh run interface '+aIntf
                                                                AEnddevice.clear_buffer()
                                                                output1 = AEnddevice.send_command(command,int(delayFactor),int(loop))
                                                                output1 = str(output1)
                                                                print "A END",output1  
                                                                
                                                                log.info("Device %s .Command (%s) output %s ",str(device1),str(command),str(output1)) 
                                                                match=re.match(r'.*ip\s+address\s+(.*)\s+255.*',output1,re.DOTALL)
                                                                if match:
                                                                                                AEndIntf=match.group(1)
                                                                                
                                                                BEnddevice = ConnectHandler(device_type="cisco_ios", ip=device2, username=username, password=password)
                                                                command='sh run interface '+bIntf
                                                                BEnddevice.clear_buffer()
                                                                output2 = BEnddevice.send_command(command,int(delayFactor),int(loop))
                                                                output2 = str(output2)
                                                                print "B END",output2  
                                                                log.info("Device %s .Command (%s) output %s ",str(device2),str(command),str(output2)) 
                                                                match=re.match(r'.*ip\s+address\s+(.*)\s+255.*',output2,re.DOTALL)
                                                                if match:
                                                                                                BEndIntf=match.group(1)
                                                                                               
                                
                                                                command='ping '+BEndIntf.strip()+' source '+AEndIntf.strip()+' repeat 30 timeout '+timeout
                                                                AEnddevice.clear_buffer()
                                                                output1 = AEnddevice.send_command(command,int(delayFactor),int(loop))
                                                                output1=str(output1)
                                                                print "Pingresult A",output1
                                                                log.info("Device %s .Ping Command (%s) output %s ",str(device1),str(command),str(output1)) 
                                                                match=re.match(r'.*rate\s+is\s+(.*)\s+percent.*',output1,re.DOTALL)
                                                                Alatency=1
                                                                pingResultA=-1
                                                                if match:
                                                                                                pingResultA=match.group(1)
                                                                                                try:
                                                                                                  if "latency" in latency:
                                                                                                    lValue=latencyValue.split(",")
                                                                                                    match1=re.match(r'.*min/avg/max\s*=\s*(\d+)/(\d+)/(\d+).*',output1,re.DOTALL)
                                                                                                    if match1:
                                                                                                        AminValue=match1.group(1)
                                                                                                        AavgValue=match1.group(2)
                                                                                                        AmaxValue=match1.group(3)
                                                                                                        if int(lValue[0]) > int(AavgValue) or int(lValue[2]) < int(AavgValue):
                                                                                                                Alatency=0
                                                                                                except Exception as e:
                                                                                                         pass         
                                                                                                    
                                                                else:
                                                                            if "Invalid" in output1:
                                                                                        pingResultA="0" 
                                                                            elif pingResultA == -1:
                                                                                    pingResultA = output1
                                                                                
                                                                                        
                                                                #command='ping '+AEndIntf.strip()+' source '+BEndIntf.strip()+' repeat 30 timeout '+timeout
                                                                command='ping '+AEndIntf.strip()+' source '+BEndIntf.strip()+'  time '+timeout+' repeat 30'
                                                                print "Ping ResultB command",command 
                                                                BEnddevice.clear_buffer()
                                                                output1 = BEnddevice.send_command(command,int(delayFactor),int(loop))
                                                                output1 = str(output1)
                                                                print "Pingresult B",output1
                                                                log.info("Device %s .Ping Command (%s) output %s ",str(device2),str(command),str(output1)) 
                                                                Blatency=1
                                                                pingResultB = -1
                                                                match=re.match(r'.*rate\s+is\s+(.*)\s+percent.*',output1,re.DOTALL)
                                                                if match:
                                                                                                pingResultB=match.group(1)
                                                                                                try:                                                           
                                                                                                  if "latency" in latency:
                                                                                                    lValue=latencyValue.split(",")
                                                                                                    match1=re.match(r'.*min/avg/max\s*=\s*(\d+)/(\d+)/(\d+).*',output1,re.DOTALL)
                                                                                                    if match1:
                                                                                                        BminValue=match1.group(1)
                                                                                                        BavgValue=match1.group(2)
                                                                                                        BmaxValue=match1.group(3)
                                                                                                        if int(lValue[0]) > int(BavgValue) or int(lValue[2]) < int(BavgValue):
                                                                                                                    Blatency=0
                                                                                                except Exception as e:
                                                                                                         pass
                                                                                                
                                                                else:
                                                                            if "Invalid" in output1:
                                                                                        pingResultB="0" 
                                                                            elif pingResultB == -1:
                                                                                        pingResultB = output1
                                                                try:      
                                                                    log.info("Ping result success rate  for A End Device : %s , For Z End Device : %s",str(pingResultA),str(pingResultB))                            
                                                                    if int(pingResultA.strip()) > 99 and  int(pingResultB.strip()) > 99:
                                                                                                if Alatency == 0 or Blatency == 0:
                                                                                                    return 0,Alatency,Blatency
                                                                                                else:
                                                                                                    return 1,Alatency,Blatency
                                                                    else:
                                                                                                return 0,Alatency,Blatency
                                                                except Exception as e:
                                                                       
                                                                                return 0,Alatency,Blatency             
                                except Exception as e:
                                                    print "msg :",str(e)  
                                                    if "Authentication" in str(e):
                                                            sendAuthFailMail(device1,device2)
                                                    elif "timed-out" in str(e):
                                                            log.info("Error occured while executing commands on Routers %s",str(e))
                                                            return 0,Alatency,Blatency
                                                            #pass   
                                                            


def PyCall():
                                    
                                    #This module calls EMC GOC hunt group number "1180"
                                    
                                callpbx = Call('SIP/emcpbx/1180', callerid = "'Syslog-Correlator' <0210>")
                                callpbxapp = Application('Playback', 'CORE-ORION-ALERTgsm')
                                cf = CallFile(callpbx, callpbxapp)
                                cf.spool()
                                
def fetchRecord(dbs):
                                                last_status_date,last_status_time,current_date,current_time=getDateandTime()
                                                from datetime import date
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
                                               # print "Table Name :",table                
                                                #LOOK FOR NEW RECORDS ON DB
                                                sqlSelect="SELECT * FROM "+table+" where (date between \'"+last_status_date+"\' AND \'"+current_date+"\') AND (time between \'"+last_status_time+"\' AND \'"+current_time+"\')";
                                                print sqlSelect
                                                log.info("Sql Statement for to fetch records between times and date %s",str(sqlSelect))
                                                cur.execute(sqlSelect)
                                                
                                                patternTagProcessed=[]
                                                for row in cur.fetchall() :
                                                                #print "row" 
                                                                host    = row[4]
                                                                message = row[7]
                                                                flag    = row[1]
                                                                #print "Before",row                                                
                                                                #IF MESSAGE AND HOST HAVE THE CORRECT STRINGS
                                                                if "orion" in host:
                                                                                if "Core-KPI-Alert" in message:  
                                                                                               # print row
                                                                                                match=re.match(r'.*-\s+(.*)\s+is.*',message,re.M|re.I)
                                                                                                if match:
                                                                                                            patTag=match.group(1)
                                                                                                            if patTag.strip() in patternTagProcessed:
                                                                                                                    log.info("Pattern tag %s is already processed then move to next record",str(patTag))
                                                                                                                    continue 
                                                                                                            else:
                                                                                                                patternTagProcessed.append(patTag)          
                                                                                                                parseMessage(message,dbs)
                                                                
def getDateandTime():
                                                import datetime
                                                                
                                                t1 = datetime.datetime.now()
                                
                                                year    = str(t1.year)
                                                month   = str(t1.month)
                                                day     = str(t1.day)
                                                hour    = str(t1.hour)
                                                minute  = str(t1.minute)
                                                second  = str(t1.second)
                                                microsecond = str(t1.microsecond)  
                                                if int(month) < 10:
                                                                month="0"+str(month)
                                                if int(day) < 10:
                                                                day="0"+str(day)
                                                if int(hour) < 10:
                                                                hour="0"+str(hour)
                                                if int(minute) < 10:
                                                                minute="0"+str(minute)
                                                if int(second) < 10:
                                                                second="0"+str(second)   
                                                current_date=year+"-"+month+"-"+day
                                                current_time=hour+":"+minute+":"+second
                                               # print current_date
                                                #print current_time
                                                
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
                                                last_status_date=""
                                                last_status_time=""
                                                #LOOK FOR NEW RECORDS ON DB
                                                cur.execute("SELECT * FROM status_time_test")
                                                for row in cur.fetchall() :
                                                                                year    = row[1]
                                                                                month   = row[2]
                                                                                day     = row[3]
                                                                                hour    = row[4]
                                                                                minute  = row[5]
                                                                                second  = row[6]
                                                                                microsecond = row[7] 
                                                                                
                                                                                if month < 10:
                                                                                                month="0"+str(month)
                                                                                if day < 10:
                                                                                                day="0"+str(day)
                                                                                if hour < 10:
                                                                                                hour="0"+str(hour)
                                                                                if minute < 10:
                                                                                                minute="0"+str(minute)
                                                                                if second < 10:
                                                                                                second="0"+str(second)
                                                                                                
                                                                                last_status_date=str(year)+"-"+str(month)+"-"+str(day)
                                                                                last_status_time=str(hour)+":"+str(minute)+":"+str(second)
                                                                                #print "last date",last_status_date
                                                                                #print "last time",last_status_time
                                                return last_status_date,last_status_time,current_date,current_time
                                                                                
                 
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
                                cur.execute("SELECT * FROM status_time_test")
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
                                                                db.autocommit(True)
                                                                cur = db.cursor()
                                                               # print "hour",hour  
                                                                #if int(hour) == 00:
                                                                 #       hour=23
                                                                #else:     
                                                                 #       hour=int(hour) - common.getTimeZoneDifferent()     
                                                                cur.execute("UPDATE status_time_test SET year="+year)
                                                                cur.execute("UPDATE status_time_test SET month="+month)
                                                                cur.execute("UPDATE status_time_test SET day="+day)
                                                                cur.execute("UPDATE status_time_test SET hour="+str(hour))
                                                                cur.execute("UPDATE status_time_test SET minute="+minute)
                                                                cur.execute("UPDATE status_time_test SET second="+second)
                                                                cur.execute("UPDATE status_time_test SET microsecond="+microsecond)
                                                                time.sleep(2)
                                                                
def TimeElapsed():
                                                                                            
                                                                #This module accesses the database for previous time call was lodged to GOC and calculated the time difference in minutes
                                                                import datetime
                                                                t1 = PreviousTime()
                                                                t2 = datetime.datetime.now()
                                                                pt = time.mktime(t1.timetuple())
                                                                ct = time.mktime(t2.timetuple())  
                                                                td = Decimal(str(ct)) - Decimal(str(pt))
                                                                scanTime = common.getScanInterval() * 60
                                                                if int(td) >= scanTime:
                                                                        return True
                                                                else:
                                                                        return False     
                                                                #return (td.days*1440)+ (td.seconds/60) + ((td.microseconds/1000/1000)/60)
                                
                                                                                            
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
                                                                                                            
                                cur.execute("SELECT enable FROM status_time_test")
                                log.info('Check CallGOCStatus is enabled or not.')                                                                            
                                for row in cur.fetchall() :
                                                                CallGOCstatus = row[0]
                
                                if (CallGOCstatus == "1"):
                                                                log.info('CallGOCStatus got enabled.')
                                                                return True
                                else:
                                                                log.info('CallGOCStatus not Enabled.')
                                                                return False
                                                                                                            
 
def intializeLoggerModule(fileName,name):
    log(fileName,name) 
    
def main():
                                                while 1:
                                                                try:
                                                                                                                           
                                                                                                dbs=createDBObject()
                                                                                                Alertmessage = OrionAlerts()                          
                                                                                                if Alertmessage == "ORION-Core-KPI-Alert":
                                                                                                                                if (TimeElapsed()) and (CallGOC()):
                                                                                                                                                                fetchRecord(dbs)
                                                                                                                                                                UpdateTime()
                                                                                
                                                                                                                            
                                                                except Exception, err:
                                                                                                sendMail("ERROR: %s\n" % str(err))
                                                                                                                            
                                                                                                                            
if __name__ == '__main__':
                                intializeLoggerModule('LogCorrelator_logger.log','LogCorrelator') 
                                main()

                                                                                                                            
                                                                                                    




