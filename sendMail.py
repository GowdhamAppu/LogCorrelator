#!/usr/bin/env python
#coding=utf-8
import subprocess
import os
import base64
import sys
import os.path
import sys
file_path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.path.pardir))
if file_path not in sys.path:
    sys.path.insert(0, file_path)
import MySQLdb
from email.mime.text import MIMEText
from pycall import CallFile, Call, Application
from datetime import datetime
import time
from Common.DBCode import DBCode
from netmiko import ConnectHandler
from multiprocessing import Process, Queue, Value, Array
import Queue as CheckQueue
import getopt
import getpass
import subprocess
import smtplib
from decimal import Decimal
import re
from Common.common import common
from Common.log import log
"""
 This method used to send mail to given mailID with proper info.
"""
def sendMail(subject,message,sev):
            try:
                smtpserver= "relay.emc-corp.net:25"
                to_addr_list = common.getEmailList(sev.lower())
                from_addr_list = "Network-engineering"
                log.info("Send mail content. Subject %s .message %s",str(subject),str(message)) 
                msg = MIMEText(message)
                msg['Subject'] = subject
                msg['From'] = from_addr_list
                msg['To'] = ",".join(to_addr_list)
                server = smtplib.SMTP(smtpserver)
                server.ehlo()
                send = server.sendmail(from_addr_list, to_addr_list, msg.as_string())
                server.quit()
            except Exception as e:
                log.warning("Send mail got error %s",str(e))
                
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

def intializeLoggerModule(fileName,name):
    log(fileName,name) 
    
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
                                                                if str(rec1[3]) == 'YES':
                                                                                #log.info('GOC Flag set as YES.so move to next record')
                                                                                continue
                                                                diff=Decimal(str(seconds)) - Decimal(str(rec1[4]))
                                                                if int(diff) >= 60:
                                                                                setFlag=[]
                                                                                SqlQuery=""
                                                                                row=db.selectCoreRouterDetails(rec1[0])
                                                                                for rec in row:
                                                                                                log.info('Going to perform ping from both ends')
                                                                                                result,AEndIntf,BEndIntf,pingA,pingB,slaState=pingTest(str(rec[10]),str(rec[11]),str(rec[5]),str(rec[7]),str(rec[12]),str(rec1[1]))
                                                                                                if result == 0:
                                                                                                                #setFlag.append(rec1[0])
                
                                                                                                                #setFlag.append('YES')
                
                                                                                                                #setFlag.append('0')
                                                                                                                if slaState.strip() == "0":
                                                                                                                    SqlQuery="update CoreCircuitStates set GOCFlag = LTRIM(\'YES\'), Time = LTRIM(\'0\') where InternalCircuitID = LTRIM(\'"+str(rec1[0])+"\')"
                                                                                                                else:
                                                                                                                    SqlQuery="update CoreCircuitStates set GOCFlag = LTRIM(\'YES\'), Time = LTRIM(\'0\') , SLAState = LTRIM(\'"+str(slaState)+"\') where InternalCircuitID = LTRIM(\'"+str(rec1[0])+"\')"
                                                                                                                phNumber=""
                                                                                                                if "NO" in str(rec[13]).strip():
                                                                                                                    phNumber=""
                                                                                                                else:
                                                                                                                    phNumber=str(rec[13]).strip()
                                                                                                                setGOCFlag(db,SqlQuery,str(rec[4]),str(rec[5]),str(rec[6]),str(rec[7]),str(rec[8]),str(rec1[2]),str(rec1[0]),AEndIntf,BEndIntf,pingA,pingB,str(rec[1]),str(rec[2]),slaState,phNumber)
                                                                                                else:
                                                                                                                log.info("Ping Result got passed.so going to delete InternalCircuitID state details from CoreCircuitState table")
                                                                                                                try:
                                                                                                                    db.deleteRow(str(rec1[0]).strip())
                                                                                                                except Exception as e:
                                                                                                                    log.warning("Error occured while deleting record in CoreCircuitStates table.Error info : %s",str(e))
                                                                                                                
                                                                                                                
                                                                                                if "down" in rec1[2]:
                                                                                                
                                                                                                                setFlag.append("UP")
                                                                                                
                                                                                                                db.updateSLAState(setFlag)
                                                                                                
                                                                                                else:
                                                                                                
                                                                                                                db.updateTime(setFlag)
                                                                                                
                
                                except Exception as e:
                                                    #log.warning("Error Occured") 
                                                    pass 
                                                #print "Exception occured ",str(e)
                
                
"""
If ping test fail then it set GOCFlag as yes and send mail to given mail ID with proper info.
"""
def setGOCFlag(db,values,val1,val2,val3,val4,val5,val6,val7,AEndIntf,BEndIntf,pingA,pingB,val8,val9,slaStates,phNumber):
            try: 
                db.updateTable(values)
                msg=""
                sev="Sev2"
                message=""
                circuitProvider=val7
                if "down" in val6.lower():
                                msg="Down"
                elif "loss" in val6.lower():
                                msg="Packet Loss. Loss Percentage is :"+val6+"%"
                else:
                                msg=slaStates
                fetchedValues,fetchedValues1,flag=db.getInternalCircuitCountMatch(val7)
                if flag:
                                circuitProvider = ""
                                sev="Sev1"
                                for val in fetchedValues:
                                                slaState=""
                                                for val1 in fetchedValues1:
                                                                if str(val[9]) == str(val1[0]):
                                                                                circuitProvider=circuitProvider+","+str(val1[0])
                                                                                if "down" in str(val1[2]).lower():
                                                                                                slaState="Down"
                                                                                elif "loss" in str(val1[2].lower()):
                                                                                                slaState="Packet Loss. Loss Percentage is :"+str(val1[2])+"%"
                                                                                else:
                                                                                                slaState=slaStates
                                                                                break
           
                                                phNumber1=""
                                                if "NO" in str(val[13]).strip():
                                                    phNumber1=""
                                                else:
                                                    phNumber1=str(val[13]).strip()
                                                message=message+"\n AEnd Device :"+str(val[4])+" Interface :"+str(val[5])+"\n ZEnd Device :"+str(val[6])+" Interface :"+str(val[7])+"\n Circuit Provider :"+str(val[8])+"\n CircuitID :"+str(val[1])+"   OrderID :"+str(val[2])+"\n SLAStatus :"+slaState+"\n Phone Number :"+phNumber1+"\n\n"
                else:
                                message="\n AEnd Device :" +val1+"  Interface : "+val2+"\n ZEnd Device :"+val3+"  Interface :"+val4+"\n Circuit Provider :"+val5+"\n CircuitID :"+val8+"  OrderID  :"+val9+"\n SLASTatus :"+msg+"\n Phone Number :"+phNumber
                                
                if pingA.strip() == "Fail":
                        message+="\n\n Access to the routers got failed due to Authentication failed."
                else:
                    try:
                        if int(AEndIntf) == 0 and int(BEndIntf) == 0 and pingA == "0" and int(pingB) == 0:
                            message+="\n\n Connection to device got timed-out"
                    except Exception as e:     
                            message+="\n\n Ping result from Device " +AEndIntf+" to Device "+BEndIntf+" \n      "+pingA+"\n\n Ping result from Device "+BEndIntf+" to Device "+AEndIntf+" \n       "+pingB+"\n\n"
                subject=sev+" Circuit ID :"+circuitProvider
                msg="Team" + "\n"+"\n"+ "Please find the details about the devices\n\n"+message   
                sendMail(subject,msg,sev)
            except  Exception as e:
                log.warning("Exception(SETGocFLag Module) message : %s",str(e))
                
def pingTest(device1,device2,aIntf,bIntf,latencyValue,latency):
                                try:
                                                                username,password=common.getRouterCredentials()
                                                                #password="WAnoharan!123"
                                                                delayFactor,loop = common.getSendCommandDelayFactor() 
                                                                timeout=getTimeout()
                                                                slaState="0"
                                                                AEnddevice = ConnectHandler(device_type="cisco_ios", ip=device1, username=username, password=password)
                                                                command='sh run interface '+aIntf
                                                                AEnddevice.clear_buffer()
                                                                output1 = AEnddevice.send_command(command,int(delayFactor),int(loop))
                                                                output1 = str(output1)
                                                                log.info("Device %s. Command %s. Output %s",str(device1),str(command),str(output1))
                                                                match=re.match(r'.*ip\s+address\s+(.*)\s+255.*',output1,re.DOTALL)
                                                                if match:
                                                                                AEndIntf=match.group(1)
                                
                                                                BEnddevice = ConnectHandler(device_type="cisco_ios", ip=device2, username=username, password=password)
                                                                command='sh run interface '+bIntf
                                                                BEnddevice.clear_buffer()
                                                                output1 = BEnddevice.send_command(command,int(delayFactor),int(loop))
                                                                output1 = str(output1)
                                                                log.info("Device %s. Command %s. Output %s",str(device2),str(command),str(output1))
                                                                match=re.match(r'.*ip\s+address\s+(.*)\s+255.*',output1,re.DOTALL)
                                                                if match:
                                                                                                BEndIntf=match.group(1)
                                                                command='ping '+BEndIntf.strip()+' source '+AEndIntf.strip()+' repeat 30 timeout '+timeout
                                                                AEnddevice.clear_buffer()
                                                                output1 = AEnddevice.send_command(command,int(delayFactor),int(loop))
                                                                output1 = str(output1)
                                                                pingA = output1
                                                                log.info("Device %s.Ping  Command %s. Output %s",str(device1),str(command),str(output1))
                                                                Alatency=1
                                                                pingResultA=-1
                                                                match=re.match(r'.*rate\s+is\s+(.*)\s+percent.*',output1,re.DOTALL)
                                                                if match:
  
                                                                                pingResultA=match.group(1)
                                                                                try:
                                                                                   if "latency" in latency.lower():
                                                                                                    lValue=latencyValue.split(",")
                                                                                                    match1=re.match(r'.*min/avg/max\s*=\s*(\d+)/(\d+)/(\d+).*',output1,re.DOTALL)
                                                                                                    if match1:
                                                                                                        AminValue=match1.group(1)
                                                                                                        AavgValue=match1.group(2)
                                                                                                        AmaxValue=match1.group(3)
                                                                                                        if int(lValue[0]) > int(AavgValue) or int(lValue[2]) < int(AavgValue):
                                                                                                                if int(lValue[0]) > int(AavgValue) and int(lValue[2]) < int(AavgValue):
                                                                                                                    slaState="Latency-Above & Below threshold"
                                                                                                                elif int(lValue[0]) > int(AavgValue):
                                                                                                                    slaState="Latency-Below threshold"
                                                                                                                else:
                                                                                                                    slaState="Latency-Above threshold"
                                                                                                                Alatency=0   
                                                                                except Exception as e:
                                                                                            log.warning("parsing Latency Message got failed.Error info : %s",str(e))
                                                                                                                                                                         
                                                                else:
                                                                                if "Invalid" in output1:
                                                                                        pingResultA="0" 
                                                                                elif pingResultA == -1:
                                                                                    pingResultA = output1                                                                              
                                                                                
                                                                               # pingResultA="0"  
                                                                command='ping '+AEndIntf.strip()+' source '+BEndIntf.strip()+' time '+timeout+' repeat 30'
                                                                BEnddevice.clear_buffer()
                                                                output1 = BEnddevice.send_command(command,int(delayFactor),int(loop))
                                                                output1 = str(output1)
                                                                pingB = output1
                                                                print "PingB",pingB
                                                                log.info("Device %s. Ping Command %s. Output %s",str(device2),str(command),str(output1))
                                                                Blatency=1
                                                                pingResultB=-1
                                                                match=re.match(r'.*rate\s+is\s+(.*)\s+percent.*',output1,re.DOTALL)
                                                                if match:
  
                                                                                pingResultB=match.group(1)
                                                                                try: 
                                                                                   if "latency" in latency.lower():
                                                                                                    lValue=latencyValue.split(",")
                                                                                                    match1=re.match(r'.*min/avg/max\s*=\s*(\d+)/(\d+)/(\d+).*',output1,re.DOTALL)
                                                                                                    if match1:
                                                                                                        BminValue=match1.group(1)
                                                                                                        BavgValue=match1.group(2)
                                                                                                        BmaxValue=match1.group(3)
                                                                                                        if int(lValue[0]) > int(BavgValue) or int(lValue[2]) < int(BavgValue):
                                                                                                                if int(lValue[0]) > int(BavgValue) and lValue[2] < int(BavgValue) :
                                                                                                                    slaState="Latency-Above & Below threshold"
                                                                                                                elif int(lValue[0]) > int(BavgValue):
                                                                                                                    slaState="Latency-Below threshold"
                                                                                                                else:
                                                                                                                    slaState="Latency-Above threshold"
                                                                                                                    Blatency=0    
                                                                                except Exception as e:
                                                                                            log.warning("parsing Latency Message got failed.Error info : %s",str(e))
                                                                                                                                                                     
                                                                else:
                                                                                if "Invalid" in output1:
                                                                                        pingResultB="0" 
                                                                                elif pingResultB == -1:
                                                                                        pingResultB = output1
                                                                try:
                                                                    log.info("Ping result success rate for A ENd Device : %s , For Z End Device : %s ",str(pingResultA),str(pingResultB))
                                                                    if int(pingResultA.strip()) > 99 and  int(pingResultB.strip()) > 99:
                                                                                if Blatency == 0 or Alatency == 0:
                                                                                    return 0,AEndIntf,BEndIntf,pingA,pingB,slaState
                                                                                else:
                                                                                    return 1,AEndIntf,BEndIntf,pingA,pingB,slaState
                                                                    else:
                                                                                return 0,AEndIntf,BEndIntf,pingA,pingB,slaState
                                                                except Exception as e:
                                                                        return 0,AEndIntf,BEndIntf,pingA,pingB,slaState
                                except Exception as e:
                                                if "Authentication" in str(e):
                                                    subject="Authentication failed on routers"+device1+","+device2
                                                    message="Error while login to Routers.Authentication failed"
                                                    sendMail(subject,message,'exception')       
                                                    return 0,0,0,"Fail",0,""                        
                                                elif "timed-out" in str(e):
                                                    log.warning("Device timed out error %s",str(e))
                                                    return 0,0,0,"0",0,""
                                                else:
                                                    log.warning("Error occured while doing pingtest %s",str(e))
                                                    
                                                
                                                                                                
if __name__=="__main__":
                intializeLoggerModule('sendMail_logger.log','sendMail') 
                db=createDBObject()
                checkAfterTimeout(db)


                                                









