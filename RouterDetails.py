#! /usr/bin/env python

# *------------------------------------------------------------------
# * RouterDetails.py  
# *
# 
# *------------------------------------------------------------------
# *@author:Gowdhaman Mohan

"""
 Importing required packages for this Apps
"""
import os.path
import sys
file_path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.path.pardir))
if file_path not in sys.path:
    sys.path.insert(0, file_path)
import hashlib
from tabulate import tabulate
from termcolor import colored
import time
from DBCode import DBCode
"""
This class is used to add and show values to/from CoreRouterDetails table.
"""
class RouterDetails:
    """
        This is a constuctor to create references object for DBCode class 
    """ 
    def __init__(self):
            self.db = DBCode()
    
    """
     Insert the values to CoreDetails table.
    """
    def insertValues(self,args):
        try:
            self.db.insertValuesIntoCoreDetailsTable(args)
        except Exception as e:
            print "Insert values got errored",str(e)
            

    """
        Delete the Internal circuit info from CoreRouterState table based on user inputs.
    """
    def deleteICID(self):
        try:
            index = 0
            icid = []
            CDetails = self.db.selectTable('CoreCircuitDetails')
            for perCore in CDetails:
                print str(index)+"."+str(perCore[9])
                index = index + 1
                icid.append(str(perCore[9]))
            icidIndex=raw_input('Select the Internal Circuit ID :')
            value=icid[int(icidIndex)]
            self.db.deleteRowCCD(value)
        except Exception as e:
            print "Error Occured while updating State Table",str(e)     
            
    """
     update the Internal circuit info from CoreCircuitDetails table based on user inputs.
    """
    def addCircuitDetails(self):
        try:
            circuitDetails=[]
            while 1:
                pTag=raw_input('Enter The Pattern Tag :')
                if pTag:
                    circuitDetails.append(str(pTag.strip()))
                    break
           
            while 1:     
                cid=raw_input('Enter The CirCuit ID :') 
                if cid:
                    circuitDetails.append(str(cid.strip()))
                    break
                         
            while 1:   
                oid=raw_input('Enter The Order ID :') 
                if oid:
                    circuitDetails.append(str(oid.strip()))
                    break
            while 1:      
                POP=raw_input('Enter The POP :') 
                if POP:
                    circuitDetails.append(str(POP.strip()))  
                    break
                
            while 1:     
                caend=raw_input('Enter The CirCuit A END :') 
                if caend:
                    circuitDetails.append(str(caend.strip()))
                    break
                
            while 1:     
                caendint=raw_input('Enter The CirCuit A End Interface  :') 
                if caendint:
                    circuitDetails.append(str(caendint.strip()))
                    break
                
            while 1:     
                czend=raw_input('Enter The CirCuit Z End  :') 
                if czend:
                    circuitDetails.append(str(czend.strip()))
                    break
                
            while 1:    
                czendint=raw_input('Enter The CirCuit Z End Interface  :') 
                if czendint:
                    circuitDetails.append(str(czendint.strip()))
                    break
                
            while 1:   
                cp=raw_input('Enter The CirCuit Provider :') 
                if cp:
                    circuitDetails.append(str(cp.strip()))
                    break
                
            while 1:   
                icid=raw_input('Enter The Internal Circuit ID :') 
                if icid:
                    circuitDetails.append(str(icid.strip()))
                    break
                
            while 1:   
                ipaddress1=raw_input('Enter The CirCuit A End Device Ipaddress :') 
                if ipaddress1:
                    circuitDetails.append(str(ipaddress1.strip()))
                    break
              
            while 1:        
                ipadd2=raw_input('Enter The CirCuit Z End Device Ipaddress :') 
                if ipadd2:
                    circuitDetails.append(str(ipadd2.strip()))
                    break
                
            while 1:     
                lv=raw_input('Enter The Latency Value(Min,Avg,Max) :') 
                if lv:
                    circuitDetails.append(str(lv.strip()))
                    break  
           
            self.db.insertValuesIntoCoreDetailsTable(circuitDetails)
        except Exception as e:
            print "Error Occured while updating State Table",str(e)        
        
            
    """
        update the Internal circuit info from CoreCircuitDetails table based on user inputs.
    """
    def updateICID(self):
        try:
            index = 0
            icid = []
            CDetails = self.db.selectTable('CoreCircuitDetails')
            for perCore in CDetails:
                print str(index)+"."+str(perCore[9])
                index = index + 1
                icid.append(str(perCore[9]))
            icidIndex=raw_input('Select the Internal Circuit ID :')
            value=icid[int(icidIndex)]
            updateValues=[]
            pTag=raw_input('Enter The Pattern Tag :')
            if pTag:
                updateValues.append('PatternTag =\''+str(pTag.strip())+'\'')
                
            cid=raw_input('Enter The CirCuit ID :') 
            if cid:
                updateValues.append(' CircuitID =\''+str(cid.strip())+'\'')  
                
            oid=raw_input('Enter The Order ID :') 
            if oid:
                updateValues.append(' OrderID =\''+str(oid.strip())+'\'')
                
            POP=raw_input('Enter The POP :') 
            if POP:
                updateValues.append(' POP =\''+str(POP.strip())+'\'')  
                
            caend=raw_input('Enter The CirCuit A END :') 
            if caend:
                updateValues.append(' CircuitAEnd =\''+str(caend.strip())+'\'')
            
            caendint=raw_input('Enter The CirCuit A End Interface  :') 
            if caendint:
                updateValues.append(' CircuitAEndIntf =\''+str(caendint.strip())+'\'')
                
            czend=raw_input('Enter The CirCuit Z End  :') 
            if czend:
                updateValues.append(' CircuitZEnd =\''+str(czend.strip())+'\'')
                
            czendint=raw_input('Enter The CirCuit Z End Interface  :') 
            if czendint:
                updateValues.append(' CircuitZEndIntf =\''+str(czendint.strip())+'\'')
                
            cp=raw_input('Enter The CirCuit Provider :') 
            if cp:
                updateValues.append(' CircuitProvider =\''+str(cp.strip())+'\'')
                
            icid=raw_input('Enter The Internal Circuit ID :') 
            if icid:
                updateValues.append(' InternalCircuitID =\''+str(icid.strip())+'\'')
             
            ipaddress1=raw_input('Enter The CirCuit A End Device Ipaddress :') 
            if ipaddress1:
                updateValues.append(' ipaddress1 =\''+str(ipaddress1.strip())+'\'')
                
            ipadd2=raw_input('Enter The CirCuit Z End Device Ipaddress :') 
            if ipadd2:
                updateValues.append(' ipaddress2 =\''+str(ipadd2.strip())+'\'')
                
            lv=raw_input('Enter The Latency Value(Min,Avg,Max) :') 
            if lv:
                updateValues.append(' LatencyValue =\''+str(lv.strip())+'\'')
                
            update=",".join(updateValues)  
            SqlUpdateQuery="update CoreCircuitDetails set %s where InternalCircuitID = \'%s\'" %(update,value)
            print SqlUpdateQuery    
            self.db.updateCCD(SqlUpdateQuery)
        except Exception as e:
            print "Error Occured while updating State Table",str(e)        
            
    """
      Fetch the data from COreDetails table and displayed to you the user
    """
    def displayValues(self):
        try:
                CDetails = self.db.selectTable('CoreCircuitDetails')
                table = []
                for perCore in CDetails:
                    table.append([perCore[0],perCore[1],perCore[2],perCore[3],perCore[4],perCore[5],perCore[6],perCore[7],perCore[8],perCore[9],perCore[10],perCore[11],perCore[12]])
                if table:
                    print tabulate(table,headers=["PatternTag","CircuitID","OrderID","POP","Circuit A End","Circuit A End Intf","Circuit Z End","Circuit Z End Intf","Circuit Provider","Internal CircuitID","IPAddress1","IPAddress2","Latency(min/avg/max)"],tablefmt="orgtbl")
                else:
                    print  colored('No data found','red')
        except Exception as e:
                print('Table doesnt exists ',str(e))
    """
     This is the main function to call respective function based on options provided through command line
    """
    def main(self,args):
        if args[0].strip() == 'show':
            self.displayValues()
        elif args[0].strip() == 'delete':
            self.deleteICID()
        elif args[0].strip() == 'update':
            self.updateICID()
        else:    
            self.addCircuitDetails()

if __name__ == '__main__':
    rObject = RouterDetails()
    rObject.main(sys.argv[1:])



