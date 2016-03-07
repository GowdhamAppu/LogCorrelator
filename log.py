#! /usr/bin/env python
# *------------------------------------------------------------------
# * log.py  
# *
# 
# *------------------------------------------------------------------
# *@author:Gowdhaman Mohan
"""
 Importing required packages for this Apps
"""

import logging
import logging.handlers
"""
This class used to update the logs in specified log file using python logging module.
"""
class log:
   logg =""
   def __init__(self,fileName,name):
      self.logger = logging.getLogger(name.strip())
      self.logger.setLevel(logging.INFO)
      if self.logger.handlers:
         log.logg = self.logger
         #print "second logger",str(log.logg)
         return
      self.logger.propagate = False
      #handler = logging.FileHandler(fileName)
      handler = logging.handlers.TimedRotatingFileHandler(fileName,"H",1,5)
      formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
      handler.setFormatter(formatter)
      self.logger.addHandler(handler)
      #logging.basicConfig(level=logging.CRITICAL,filename=fileName,format='%(asctime)s %(message)s', filemode='w') 
      log.logg = self.logger
      #print "logger handle %s"%str(log.logg)
   
   	  
   @staticmethod
   def info(msg,*variable):
      if variable:
	 log.logg.info(msg, *variable)
      else:
	 log.logg.info(msg)
        
		
   @staticmethod	  
   def debug(msg,*variable):
      if variable:
	 log.logg.debug(msg, *variable)   
      else:
	 log.logg.debug(msg)
	   
   @staticmethod	  
   def critical(msg,*variable):
      if variable:
	 log.logg.critical(msg, *variable)
      else:
	 log.logg.critical(msg)
		
   @staticmethod	  
   def error(msg,*variable):
      if variable:
	 log.logg.error(msg, *variable)   
      else:
	 log.logg.error(msg)
	   
   @staticmethod	  
   def warning(msg,*variable):
      if variable:
	 log.logg.warning(msg, *variable)
      else:
	 log.logg.warning(msg) 	  
    	  

