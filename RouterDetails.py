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
      Fetch the data from COreDetails table and displayed to you the user
    """
    def displayValues(self):
        try:
                CDetails = self.db.selectTable('CoreCircuitDetails')
                table = []
                for perCore in CDetails:
                    table.append([perCore[0],perCore[1],perCore[2],perCore[3],perCore[4],perCore[5],perCore[6],perCore[7],perCore[8],perCore[9],perCore[10],perCore[11]])
                if table:
                    print tabulate(table,headers=["PatternTag","CircuitID","OrderID","POP","Circuit A End","Circuit A End Intf","Circuit Z End","Circuit Z End Intf","Circuit Provider","Internal CircuitID","IPAddress1","IPAddress2"],tablefmt="fancy_grid")
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
        else:
            self.insertValues(args[1:])

if __name__ == '__main__':
    rObject = RouterDetails()
    rObject.main(sys.argv[1:])

