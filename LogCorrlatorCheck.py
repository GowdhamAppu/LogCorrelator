#! /usr/bin/env python

# *------------------------------------------------------------------
# * LogCorrelatorCheck.py  
# *
# 
# *------------------------------------------------------------------
# *@author:Gowdhaman Mohan
"""
 Importing required packages for this Apps
"""
import sys
import re
from termcolor import colored
import subprocess
import time
import os,signal

class LogCorrelator:
    """
    Check the process status before starting the processes
    """
    @staticmethod
    def check(process,supress = 1): 
        out=[]
        try:
            P = subprocess.Popen(process, stdout=subprocess.PIPE,shell=True)
           # time.sleep(1)
            output,err = P.communicate()
            out = output.split('\n')
           # print out
            if len(out) > 3:
                for line in out:
                    if re.match(".*\s+(R|Rl|T|Tl|S|Sl|S+)\s+.*", line):
                        if supress == 0:
                            print "1"  
                        return 1,out
                return -1,out
            else:
                if supress == 0:
                    print "0"
                return 0,out
        except Exception as e:
            return 1,out
		   
    """
    Kill the specified process
    """
    @staticmethod
    def killProcess(out):
        for line in os.popen(out):
		   fields = line.split()
		   pid = fields[0]
                   os.kill(int(pid),signal.SIGKILL)
                   print "Process Killed Successfully"		   
     
if __name__ == '__main__':
    if sys.argv[1] == "check":
          #time.sleep(2)  
          ret,out=LogCorrelator.check('ps aux | grep \"python -W ignore /opt/CoreMonitoringApp/LogCorrelator.py\"',0)
    else:	  
          #time.sleep(2)
          LogCorrelator.killProcess('ps ax | grep \"python -W ignore /opt/CoreMonitoringApp/LogCorrelator.py\" | grep -v grep')
        

