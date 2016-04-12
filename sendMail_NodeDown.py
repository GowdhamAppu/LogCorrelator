
import os.path
import sys
file_path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.path.pardir))
if file_path not in sys.path:
    sys.path.insert(0, file_path) 
import time
from datetime import datetime
from Common.DBCode import DBCode
from Common.common import common
from decimal import Decimal
from Common.log import log
import smtplib
import commands as cm

from email.mime.text import MIMEText
"""
This method used to create references to the DBCode class.
"""
def createDBObject():
                try:
                                db = DBCode()
                                return db
                except Exception as e:
                                log.warning("NodeDown -- Exception occured during Database Connection %s",str(e))
                                
def checkDataBase(dbs):
                
                try:
                                record=dbs.selectTable('nodeState')
                                for rec in record:
                                                                flag=str(rec[3])
                                                                if flag.strip() == 'YES':
                                                                                Count=len(str(rec[2]).split(','))
                                                                                if int(Count) == 1:
                                                                                                result=nodePingtest(str(rec[4]).strip())
                                                                                                if result == "0":
                                                                                                                log.info("Skipping mail operations and delete info from nodeState table.")
														self.db.deleteRowNode(str(rec[0]))
														print 'Node  info got deleted.',str(rec[0])
														continue
												elif result == "1":
														msg=""
														subject="Sev2 Node Down, Device-Type :"+str(rec[5])+", City:"+str(rec[0])
														msg+="    Device Name :"+str(rec[2])+"   IP-Address :"+str(rec[4])+"  Device-Type : Core City : "+str(rec[0])+"  State : Packet Loss\n     Ping Result \n  Got exception while doing ping test, please refer logs for more info "
														
														message="Team \n\n\n Please investigate this node down incident \n\n "+msg							
												else:
														msg=""
														subject="Sev2 Node Down, Device-Type :"+str(rec[5])+", City:"+str(rec[0])
														msg+="    Device Name :"+str(rec[2])+"   IP-Address :"+str(rec[4])+"  Device-Type : Core City : "+str(rec[0])+"   State : Packet Loss\n     Ping Result \n               "+str(result)
														message="Team \n\n\n Please investigate this node down incident \n\n "+msg
                                                                                else:
                                                                                               # subject="Sev1 Nodes Down, Device-Type :"+str(rec[5])+" ,City:"+str(rec[0])
                                                                                                nodeNames=str(rec[2]).split(',')
                                                                                                ipadd=str(rec[4]).split(',')
                                                                                                msg=""
												removeNodes=[]
												counting=0
                                                                                                for i in range(0,len(nodeNames)):
														result=nodePingtest(str(ipadd[i]).strip())
														if result == "0":
																removeNodes.append(str(nodeNames[i]))
														elif reult == "1":
																counting = counting + 1
																msg+="    Device Name :"+str(nodeNames[i])+"   IP-Address :"+str(ipadd[i])+"  Device-Type : Core City : "+str(rec[0])+"  State : Packet Loss\n   Ping Result \n   Got exception while doing ping test, please refer logs for more info "
														else:		
																counting=counting+1
																msg+="    Device Name :"+str(nodeNames[i])+"   IP-Address :"+str(ipadd[i])+"  Device-Type : Core City : "+str(rec[0])+"  State : Packet Loss \n   Ping Result \n                "+str(result)
												if counting > 1:				
														subject="Sev1 Nodes Down, Device-Type :"+str(rec[5])+" ,City:"+str(rec[0])  
												elif counting == 1:
														subject="Sev2 Nodes Down, Device-Type :"+str(rec[5])+" ,City:"+str(rec[0]) 
												else:
														log.info("Skipping mail operations and delete info from nodeState table.")
														self.db.deleteRowNode(str(rec[0]))
														print 'Node  info got deleted.',str(rec[0])
														continue
												message="Team \n\n\n Please find details about down nodes \n\n "+msg
												if removeNodes:
														dbNodeValue=str(rec[2]).split(",")
														dbIpaddress=str(rec[4]).split(",")
														for node in removeNodes:
																index=dbNodeValue.index(str(node)) 
																del dbIpaddress[index]    
																dbNodeValue.remove(str(node))
																
														value=",".join(dbNodeValue)
														Count1=len(dbNodeValue)
														ipadd=",".join(dbIpaddress)
														values=[]
														values.append(str(rec[0]))
														values.append(str(Count1))
														values.append(str(value))
														values.append('NO')
														values.append(str(ipadd))
														dbs.updateNodeStateTable(values)  
														print'Node record got updated.values are',str(values)
														sendMail(subject,message)
														continue
														                                                                       
                                                                                sendMail(subject,message)
                                                                                value=[]
                                                                                value.append(str(rec[0]))
                                                                                value.append('NO')
                                                                                dbs.updateNodeStateTableAfterMailSend(value)
                                            
                except Exception as e:
                                log.warning("Node Down-- Exception occured(CheckDatabse Module). Error info : %s",str(e))
                
                               

def  nodePingtest(ipaddress):
                try:
                                status,result=cm.getstatusoutput("ping -c100 "+str(ipaddress))
                                log.info("Node ping result : %s",str(result))
                                if status == 0:
                                                log.info("Ping to device got passed")
                                                return "0"
                                else:                                
                                                return str(result)
                except Exception as e:
                                log.warning("Ping test for Node Reboot got exception . Error msg : %s",str(e))
                                return "1"

def getTime():
                dt=datetime.today()
                seconds=time.mktime(dt.timetuple())
                return seconds   

                                                             

def sendMail(subject,message):
                try:
                                smtpserver= "relay.emc-corp.net:25"
                                #to_addr_list = ["Gowdhaman.Mohan@emcconnected.com"] 
                                to_addr_list = common.getEmailList('exception')
                                from_addr_list = "Network-engineering"
                                log.info("Node -- Send mail content. Subject %s .message %s",str(subject),str(message)) 
                                msg = MIMEText(message)
                                msg['Subject'] = subject
                                msg['From'] = from_addr_list
                                msg['To'] = ",".join(to_addr_list)
                                server = smtplib.SMTP(smtpserver)
                                server.ehlo()
                                send = server.sendmail(from_addr_list, to_addr_list, msg.as_string())
                                log.info("Node-- Mail has been sent to %s",str(to_addr_list))
                                server.quit()
                except Exception as e:
                                log.warning("Node -- Send mail got error %s",str(e)) 
                                
def intializeLoggerModule(fileName,name):
                log(fileName,name) 
    
def main(startingTime,interval,db):
                while 1:
                                presentTime=getTime()
                                diff=Decimal(str(presentTime)) - Decimal(str(startingTime))
                                if int(diff) >= interval:
                                                checkDataBase(db)     
                                                startingTime=getTime()     
        
    
if __name__ == "__main__":
                #intializeLoggerModule("NodeChecking_logger.log","NodeCheck")
                intializeLoggerModule('sendMail_logger.log','sendMail')
                db=createDBObject()            
                interval=common.getNodeCheckInterval()
                interval=interval*60
                startTime=getTime()
                main(startTime,interval,db)



