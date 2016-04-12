#! /usr/bin/env python

# *------------------------------------------------------------------
# * RouterStateDetails.py  
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
This class used to show/delete the Internal Circuit details to/from CoreRouterState table.
"""
class RouterStateDetails:
            """
              Create references to DBCode class.
            """
            def __init__(self):
                    self.db = DBCode()
            
            """
             Delete the Internal circuit info from CoreRouterState table based on user inputs.
            """
            def deleteICID(self):
                    try:
                        index = 0
                        icid = []
                        CDetails = self.db.selectTable('CoreCircuitStates')
                        for perCore in CDetails:
                            print str(index)+"."+str(perCore[0])
                            index = index + 1
                            icid.append(str(perCore[0]))
                        if CDetails:    
                            icidIndex=raw_input('Select the Internal Circuit ID :')
                            value=icid[int(icidIndex)]
                            self.db.deleteRow(value)
                        else:
                            print "No data in circuit state table"
                    except Exception as e:
                        print "Error Occured while updating State Table",str(e)
                        
            def deleteNode(self):
                index=0
                nodeNames = []
		cityNames = []
                NDetails = self.db.selectTable('nodeState')
                for perNode in NDetails:
                    nodes=str(perNode[2]).split(",")
                    for node in nodes:
                        print str(index)+"."+str(node)
                        index = index + 1
                        cityNames.append(str(perNode[0]))
			nodeNames.append(str(node))
                if nodeNames:
			cIndex=raw_input('Select the Node to be deleted :')
			value=cityNames[int(cIndex)]
			node=nodeNames[int(cIndex)]
			record=self.db.selectNodeState(str(value).strip())
			dbNodeValue=""
			dbIpaddress=""
			print "yet to delete nodes : -",nodes
			for rec in record:
							dbNodeValue=str(rec[2]).split(",")
							dbIpaddress=str(rec[4]).split(",")
							print "DBNode",dbNodeValue
							#for node in nodes:
							if node in str(rec[2]).strip():
								    index=dbNodeValue.index(str(node)) 
								    del dbIpaddress[index]    
								    dbNodeValue.remove(str(node))
							if dbNodeValue:
								    value=",".join(dbNodeValue)
								    Count=len(dbNodeValue)
								    ipadd=",".join(dbIpaddress)
								    values=[]
								    values.append(str(rec[0]))
								    values.append(str(Count))
								    values.append(str(value))
								    values.append('NO')
								    values.append(str(ipadd))
								    self.db.updateNodeStateTable(values)  
								    print'Node record got updated.values are',str(values)
							else:
								    self.db.deleteRowNode(str(rec[0]))
								    print 'Node  info got deleted.',str(rec[0])                     
            """
             Display all records in CoreRouterState table.
            """
            def displayValues(self):
                            try:
                                    CDetails = self.db.selectTable('CoreCircuitStates')
                                    table = []
                                    for perCore in CDetails:
                                        table.append([perCore[0],perCore[1],perCore[2],perCore[3]])
                                    if table:
                                        print tabulate(table,headers=["Internal CircuitID","Issue Type","SLA State","GOC Flag"],tablefmt="fancy_grid")
                                    else:
                                        print  colored('No data found','red')
                            except Exception as e:
                                    print('Table doesnt exists ',str(e))
            
            """
                Display all records in nodeState table.
            """
            def displayNodeStates(self):
                            try:
                                    CDetails = self.db.selectTable('nodeState')
                                    table = []
                                    for perCore in CDetails:
					if str(perCore[3]).strip() == "YES":
					    table.append([perCore[0],perCore[1],perCore[2],"NO"])
					else:
					    table.append([perCore[0],perCore[1],perCore[2],"YES"])
                                    if table:
                                        print tabulate(table,headers=["Node Common Name","Number Of Nodes Down","Actual Nodes","GOC Flag"],tablefmt="fancy_grid")
                                    else:
                                        print  colored('No data found','red')
                            except Exception as e:
                                    print('Table doesnt exists ',str(e)) 
             
            def deleteOptions(self):
                print "Choose one"
                print "1.Delete from Circuit State table"
                print "2.Delete from Node State table"
                opt=raw_input('Select the option :')
                if int(opt) == 1:
                    self.deleteICID()
                elif int(opt) == 2:
                    self.deleteNode()
                else:
                    print "Choose either 1/2"
                    
            def displayOptions(self,options):
                if int(options) == 1:
                        self.displayValues()
                elif int(options) == 2:
                        self.displayNodeStates() 
                elif int(options) == 3:
                        self.displayValues()
                        print("---------------------------------------------------------------------------------------------------------------------")
                        self.displayNodeStates() 
                else:
                        print("Choose either 1/2/3")
                
            def main(self,args):
                            try:
                                if args[0].strip() == 'show':
                                    print "Choose one :"
                                    print "   1. SLAStates"
                                    print "   2. NodeStates "
                                    print "   3. Both        "
                                    opt=raw_input('Select the option :')
                                    self.displayOptions(int(opt))
                            except Exception as e:
                                    self.deleteOptions()
                       
if __name__ == '__main__':
    rObject = RouterStateDetails()
    rObject.main(sys.argv[1:])
               
     


