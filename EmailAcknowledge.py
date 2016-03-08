#!/usr/bin/env python
#coding=utf-8
import imaplib
from DBCode import DBCode
from log import log

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
                                
                                
def read(username, password,db):
                                # Login to INBOX
                                imap = imaplib.IMAP4_SSL("outlook.office365.com", 993)
                                imap.login(username, password)
                                imap.select('INBOX')
                                while 1:
                                                                for line in open('mailIDFile','r').readlines():
                                                                    # Print all unread messages from a certain sender of interest
                                                                                                emailID=str(line).strip()
                                                                                                print "MailID",line.strip()
                                                                                                status, response = imap.search(None, '(UNSEEN)', '(FROM "%s")' % (emailID))
                                                                                                unread_msg_nums = response[0].split()
                                                                                                
                                                                                                for e_id in unread_msg_nums:
                                                                                                    #print "full msg : ",e_id
                                                                                                                                                                                                                                                              
                                                                                                                                _, response = imap.fetch(e_id, '(UID BODY[TEXT])')
                                                                                                                                subject=0
                                                                                                                                body=0
                                                                                                                                flag=0
                                                                                                                                typemsg,data = imap.fetch(e_id,'(RFC822.SIZE BODY[HEADER.FIELDS (SUBJECT)])')
                                                                                                                                subject = data[0][1].lstrip('Subject: ').strip() + ' '
                                                                                                                                body = response[0][1]
                                                                                                                                print body
                                                                                                                                print subject
                                                                                                                                if subject == 0:
                                                                                                                                                                pass
                                                                                                                                else:
                                                                                                                                                                circuitIDs=subject.split(",")
                                                                                                                                                                log.info("CIrcuit IDs : %s",str(circuitIDs))
                                                                                                                                                                #print circuitIDs[1]
                                                                                                                                if body == 0:
                                                                                                                                                                pass
                                                                                                                                else:
                                                                                                                                                                if "acknowledge" in body.lower():
                                                                                                                                                                                                flag = 1
                                                                                                                                                                                                log.info("Acknowledge string present in the Body message: %s",str(body))
                                                                                                                                if flag == 1:
                                                                                                                                                                CIDs=circuitIDs[1:]
                                                                                                                                                                print CIDs
                                                                                                                                                                log.info("Going to delete CircuitID record from CoreCircuitState table which has been resolved .")
                                                                                                                                                                for cid in CIDs:
                                                                                                                                                                                                db.deleteRow(cid.strip())
                                                                                                                                                                                                log.info("Record Deleted Successfully ")
                       # print "Internal Circuit ID "+cid.strip()+" Record Deleted Succeffully from mCoreCircuitStates Table"    
                                                                                                #db.deleteRow(value)       
                                                                                                # Mark them as seen
                                                                                                for e_id in unread_msg_nums:
                                                                                                                                imap.store(e_id, '+FLAGS', '\Seen')
                                            
if __name__ == "__main__":
                                initialize('EmailAcknowledge_logger.log','Email') 
                                db= createDBObject()
                                read('Gowdhaman.Mohan@emcconnected.com','**',db)

