#!/usr/bin/env python
#coding=utf-8
import os.path
import sys
file_path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.path.pardir))
if file_path not in sys.path:
    sys.path.insert(0, file_path)
import imaplib
from Common.DBCode import DBCode
from Common.log import log
import re
from Common.common import common
import hashlib
import smtplib
from email.mime.text import MIMEText

def sendMail(subject,message,to_addr_list):
				try:
								smtpserver= "relay.emc-corp.net:25"
								#to_addr_list = common.getEmailList(sev.lower())
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
								log.warning("Exception occured during send mail . Error Msg : %s",str(e))
												
								
"""
 To intialize Logger module
"""
def initialize(filename,name):
                                log(filename,name)

"""
 To create refernces for DBCode class 
"""
def createDBObject():
                                try:
                                                                db = DBCode()
                                                                return db
                                except Exception as e:
                                                                log.warning("Exception occured during Database Connection %s",str(e))
def delete(city,nodes,dbs):
				try:
								print "city",city
								record=dbs.selectNodeState(city.strip())
								dbNodeValue=""
								print "yet to delete nodes : -",nodes
								for rec in record:
												dbNodeValue=str(rec[2]).split(",")
												dbIpaddress=str(rec[4]).split(",")
												print "DBNode",dbNodeValue
												for node in nodes:
																if str(node).strip() in str(rec[2]).strip():
																				index=dbNodeValue.index(str(node).strip()) 
																				del dbIpaddress[index]
																				
																				dbNodeValue.remove(str(node).strip())
																				print "DBNode:",dbNodeValue
												if dbNodeValue:
																value=",".join(dbNodeValue)
																Count=len(dbNodeValue)
																ipadd=",".join(dbIpaddress)
																values=[]
																values.append(str(rec[0]))
																values.append(Count)
																values.append(str(value))
																values.append('NO')
																values.append(str(ipadd))
								                                                                dbs.updateNodeStateTable(values)  
																log.info('Node record got updated.values are %s',str(values))
												else:
																dbs.deleteRowNode(str(rec[0]))
																log.info('Node %s info got deleted.',str(rec[0]))
												
													
				except Exception as e:
								log.warning("Exception occured while deleting records.Error info %s",str(e))  
		       
def deleteDetails(subject,body,db):
				try:
								city=""
								nodeList=""
								match=re.match(r'.*City:(.*)',str(subject),re.M|re.I)
								if match:
												city=match.group(1)
												#nodeList=str(match.group(2)).split(",")
								else:
												return 0
				                                
								bodyMsg=body.split("\n")
								for line in bodyMsg:
												if "node" in line.lower():
																match=re.match(r'.*Nodes\s*Down\s*:(.*)<o:p>.*',str(line),re.DOTALL)
																if match:
																				nodes=match.group(1)
																				nodes=nodes.split(",")
																				delete(city,nodes,db)
																				return 1
																				
																else:
																				log.warning("Parsing bosy message doesn't match pattern. Body message %s",str(body))
																				return 0
																				
																				
																 
								
				except Exception as e:
								log.info("Exception occured while deleting records .Error info %s",str(e))
								return -1
               		
def read(username, password,db):
                # Login to INBOX
				
				imap = imaplib.IMAP4_SSL("outlook.office365.com", 993)
				imap.login(username, password)
				imap.select('EMC-Core-Mon')
						#imap.select('INBOX')
				
				for line in open('/opt/CoreMonitoringApp/Common/secretKey','r').readlines():
														# Print all unread messages from a certain sender of interest
												passwordStr=str(line).strip()
												#print "MailID",line.strip()
												hash_object=hashlib.md5(passwordStr.encode())
												hashPass=hash_object.hexdigest()
												status, response = imap.search(None, '(UNSEEN)')
												unread_msg_nums = response[0].split()
																		   
												for e_id in unread_msg_nums:
												    #print "full msg : ",e_id
																																								   
																_, response = imap.fetch(e_id, '(UID BODY[TEXT])')
																subject=0
																body=0
																flag=0
																fromMailID=""
																typemsg,data = imap.fetch(e_id,'(RFC822.SIZE BODY[HEADER.FIELDS (SUBJECT)])')
																subject = data[0][1].lstrip('Subject: ').strip() + ' '
																body = response[0][1]
																typemssg,data= imap.fetch(e_id,'(RFC822.SIZE BODY[HEADER.FIELDS (FROM)])')
																fromMailID = data[0][1].lstrip('From: ').strip()
																print "From MailID :-",fromMailID
																mailID=""
																match=re.match(r'\s*\"(.*)\"\s*\<.*',str(fromMailID),re.M|re.I)
																nodeStringPresent=0
																cidStringPresent=0
																if match:
																				mailID=str(match.group(1).strip())
																		
																else:
																				mailID=fromMailID
																#print body
																print subject
																print "hashvalue",hashPass
																mdHash=0
																mdStringPresent=0
																if "md5" in str(body).lower():
																				bodyMsg=body.split("\n")
																				for line in bodyMsg:
																												#print "line",line
																												if "md5" in line.lower():
																																mdStringPresent = 1
																																match=re.match(r'.*MD5hash\s*:(\s*.*<span.*white">|\s*)([a-zA-Z0-9]+)(</span><o:p>.*|</span><span .*>.*|<o:p>)',str(line),re.M|re.I)
																																if match:
														
																																				hashValue=str(match.group(2)).strip()
																																				print hashValue
																																				print hashPass
																																				if hashValue.strip() == hashPass.strip():
																																								mdHash=1
																																								print "matched",mdHash
																																								break
																																				
								 
																if mdHash == 0:
																				if mdStringPresent == 0:
																								to_addr_list=str(common.getAdditionalMailID()).split(",")
																								to_addr_list.append(str(fromMailID))
																								#to_addr_list.append('goc@emcconnected.com')
																								subjectHeading=subject
																								message="Hi "+mailID+",\n\n The MD5 Hash key is missing from the email sent,Please add the correct MD5 Hash when sending the Acknowledgement Mail.\n\n\n Example: MD5hash: XXXXXXXXXXXXXXXXXXXXXXXX \n\n Thanks\n Core Montiorng App\n network-eng@emcconnected.com"
																								sendMail(subjectHeading,message,to_addr_list)
																				else:
																								
																								print mdHash
																								to_addr_list=str(common.getAdditionalMailID()).split(",")
																								to_addr_list.append(str(fromMailID))
																								#to_addr_list.append('goc@emcconnected.com')
																								subjectHeading=subject
																								message="Hi "+mailID+",\n\n The MD5 HASH sent for the acknowledge of Circut ID doesn't match.Please enter the correct MD5 hash.Please do not reply to this email.\n\n Thanks\n Core Montirong App\n network-eng@emcconnected.com"
																								sendMail(subjectHeading,message,to_addr_list)
																								log.warning('Unable to match MDSHash value.Please use proper hash value in the mail.')
																								continue
																																																		      
																																												    #print circuitIDs[1]
																																				
																 						
																if "acknowledge" in str(body).lower():
																				flag = 1
																				log.info("Acknowledge string present in the Body message: ")
																																						
																if flag == 1:
																				if "node" in str(subject).lower():
																								nodeStringPresent=1
																								success=deleteDetails(subject,body,db)
																								if success == 0:
																												to_addr_list=str(common.getAdditionalMailID()).split(',')
																												to_addr_list.append(str(fromMailID))
																												subjectHeading="Nodes Down,Device-Type: XXXXXX, City: XXXXXXXX"
																												message="Hi "+str(mailID)+", \n\n The EMail Acknowledge format for Node Down is like below. \n\n  Nodes Down:XXXX,XXXXX\n  Status: Acknowledge\n  MD5hash: xxxxxxxxxxxxxxxxxx.Please do not reply to this mail. \n\n Thanks\n Core Motinoring App\n network-eng@emcconnected.com"
																												sendMail(subjectHeading,message,to_addr_list)
																												
																				else:  
																								
																								#bodyMsg=body.split("\n")
																								#for line in bodyMsg:
						
						 																						match=re.match(r'(.*Circuit\s*ID\s*|[a-zA-Z]*\s*:\s*CID|\s*CID\s*):(.*)',str(subject),re.M|re.I)
																																															#print "line",line
																																					  
																												if match:			         
																																circuitIDs=str(match.group(2)).split(',')																										
																																CIDs=circuitIDs
																																
																																#print CIDs
																																#log.info("Going to delete CircuitID record from CoreCircuitState table which has been resolved .")
																																for cid in CIDs:
																																				check=db.checkInTable(str(cid).strip())
																																				if int(check) == 1:
																																								db.deleteRow(cid.strip())
																																								log.info("Record Deleted Successfully. Internal Circuit Id : %s ",str(cid))														
																																				else:
																		
																		
																																								
																																								#sendMail()
																																								to_addr_list=str(common.getAdditionalMailID()).split(",")
																																								to_addr_list.append(fromMailID)
																																								#to_addr_list.append('goc@emcconnected.com')
																																								subject="Circuit ID:"+str(cid)
																																								message=" Hi Team, \n\n   The Circuit ID  sent "+str(cid)+" for acknowledgement does not exists in the Circuit State Table.Please enter the correct CircuitID or check if the incident has already been approved.\n\n\n Thanks,\n Core Monitoring App\n network-eng@emcconnected.com "
																																								sendMail(subject,message,to_addr_list)
																																																							    
																												else:
										
																																to_addr_list=str(common.getAdditionalMailID()).split(',')
																																to_addr_list.append(str(fromMailID))
																																subjectHeading=subject
																																message="Hi "+str(mailID)+"\n\n The subject mail should like either \"Circuit ID: XXXXXXXXXXXXXXXXXX\" or \"CID: XXXXXXXXXXXXXXX\". Please check the Email Acknowledge mail format and send.\n\n Thanks\n Core Monitoring App\n network-eng@emcconnected.com"
																																sendMail(subjectHeading,message,to_addr_list)
																																
																																																																							
																						    # print "Internal Circuit ID "+cid.strip()+" Record Deleted Succeffully from mCoreCircuitStates Table"    
																								    #db.deleteRow(value)       
																						       # Mark them as seen
												for e_id in unread_msg_nums:
																imap.store(e_id, '+FLAGS', '\Seen')
												    
if __name__ == "__main__":
                                initialize('EmailAcknowledge_logger.log','Email') 
                                db= createDBObject()
				while 1:
								read('paul.vijay@emc-corp.net','WAnoharan!123',db)
				






