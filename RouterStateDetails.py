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
                        icidIndex=raw_input('Select the Internal Circuit ID :')
                        value=icid[int(icidIndex)]
                        self.db.deleteRow(value)
                    except Exception as e:
                        print "Error Occured while updating State Table",str(e)
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
                       
            def main(self,args):
                            try:
                                if args[0].strip() == 'show':
                                    self.displayValues()
                            except Exception as e:
                                    self.deleteICID()
                       
if __name__ == '__main__':
    rObject = RouterStateDetails()
    rObject.main(sys.argv[1:])
               
     
