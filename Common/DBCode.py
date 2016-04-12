#! /usr/bin/env python

# *------------------------------------------------------------------
# * DBCode.py  
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
    
import sqlalchemy.pool as pool
import mysql.connector


def getconn():
    c = mysql.connector.connect(user='root', password='De7lc3-S!!',database='LogCorrelator')
    return c

class DBCode:
    dbConnectionPool = None

    def __init__(self):
        try:
            DBCode.dbConnectionPool = pool.QueuePool(getconn, max_overflow=20, pool_size=15,echo=True)
        except mysql.connector.Error as err:
            log.error('MySql Error: Exception occured due to Database doesnt exists or MySql Credentials error %s',str(err))

    def getConnection(self):
                    try:
                        conn = DBCode.dbConnectionPool.connect()
                        return conn
                    except mysql.connector.Error as err:
                        log.error('300000: MySql Error: Exception occured due to Database doesnt exists or MySql Credentials error %s',str(err))
                        return None
                    
    def insertValuesintonodeStateTable(self,values):
                        SqlInsertQuery = "insert into nodeState (nodeCommonName,Count,ActualNodes,flag,ipaddress,CustomerType) " \
                                      "values (LTRIM(\"%s\"),LTRIM(\"%s\"),LTRIM(\"%s\"),LTRIM(\"%s\"),LTRIM(\"%s\"),LTRIM(\"%s\")) "\
                                     %(values[0],values[1],values[2],values[3],values[4],values[5])
                        lockQuery = " LOCK TABLES nodeState WRITE"
                        releaseLocks = " UNLOCK TABLES"
                        connecTion = self.getConnection()
                        if connecTion:
                            try:
                                cursor = connecTion.cursor()
                                cursor.execute(lockQuery)
                                cursor.execute(SqlInsertQuery)
                                cursor.execute(releaseLocks)
                                connecTion.commit()
                                cursor.close()
                                print("Record Inserted")
                            except mysql.connector.Error as err:
                                cursor.execute(releaseLocks)
                                cursor.close()
                                raise Exception(err)
                        else:
                            print("Error while connecting to MySql")            
        
    def insertValuesIntoCoreDetailsTable(self,values):
                        SqlInsertQuery = "insert into CoreCircuitDetails (PatternTag,CircuitID,OrderID,POP,CircuitAEnd,CircuitAEndIntf,CircuitZEnd,CircuitZEndIntf,CircuitProvider,InternalCircuitID,ipaddress1,ipaddress2,LatencyValue,phoneNumber) " \
                                      "values (LTRIM(\"%s\"),LTRIM(\"%s\"),LTRIM(\"%s\"),LTRIM(\"%s\"),LTRIM(\"%s\"),LTRIM(\"%s\"),LTRIM(\"%s\"),LTRIM(\"%s\"),LTRIM(\"%s\"),LTRIM(\"%s\"),LTRIM(\"%s\"),LTRIM(\"%s\"),LTRIM(\"%s\"),LTRIM(\"%s\")) "\
                                     %(values[0],values[1],values[2],values[3],values[4],values[5],values[6],values[7],values[8],values[9],values[10],values[11],values[12],values[13])
                        lockQuery = " LOCK TABLES CoreCircuitDetails WRITE"
                        releaseLocks = " UNLOCK TABLES"
                        connecTion = self.getConnection()
                        if connecTion:
                            try:
                                cursor = connecTion.cursor()
                                cursor.execute(lockQuery)
                                cursor.execute(SqlInsertQuery)
                                cursor.execute(releaseLocks)
                                connecTion.commit()
                                cursor.close()
                                print("Record Inserted")
                            except mysql.connector.Error as err:
                                cursor.execute(releaseLocks)
                                cursor.close()
                                raise Exception(err)
                        else:
                            print("Error while connecting to MySql")
                                                
    def insertValuesIntoCoreRouterStateTable(self,values):
                SqlInsertQuery = "insert into CoreCircuitStates (InternalCircuitID,IssueType,SLAState,GOCFlag) " \
                              "values (LTRIM(\"%s\"),LTRIM(\"%s\"),LTRIM(\"%s\"),LTRIM(\"%s\")) "\
                             %(values[0],values[1],values[2],values[3])
                lockQuery = " LOCK TABLES CoreCircuitStates WRITE"
                releaseLocks = " UNLOCK TABLES"
                connecTion = self.getConnection()
                if connecTion:
                    try:
                        cursor = connecTion.cursor()
                        print("Inserting record : %s",SqlInsertQuery)
                        cursor.execute(lockQuery)
                        cursor.execute(SqlInsertQuery)
                        cursor.execute(releaseLocks)
                        connecTion.commit()
                        cursor.close()
                        print("Record Inserted")
                    except mysql.connector.Error as err:
                        cursor.execute(releaseLocks)
                        cursor.close()
                        raise Exception(err)
                else:
                    print("Error while connecting to MySql")
                    
    def getInternalCircuitCountMatch(self,value):
            SqlSelectQuery = "select count(InternalCircuitID) from CoreCircuitDetails where POP=(select POP from CoreCircuitDetails where InternalCircuitID=LTRIM(\'%s\'))" %(value)
            
            SqlSelectQuery1= "select count(InternalCircuitID) from CoreCircuitStates where InternalCircuitID in (select InternalCircuitID from CoreCircuitDetails where POP=(select POP from CoreCircuitDetails where InternalCircuitID=LTRIM(\'%s\')))" %(value)
            
            SqlSelectQuery2 = "select * from CoreCircuitDetails where POP=(select POP from CoreCircuitDetails where InternalCircuitID=LTRIM(\'%s\'))" %(value)
            
            SqlSelectQuery3= "select * from CoreCircuitStates where InternalCircuitID in (select InternalCircuitID from CoreCircuitDetails where POP=(select POP from CoreCircuitDetails where InternalCircuitID=LTRIM(\'%s\')))" %(value)
            
            connecTion = self.getConnection()
            lockQuery = " LOCK TABLES CoreCircuitDetails READ"
            releaseLocks = " UNLOCK TABLES"
            returnVal = []
            returnVal1 = []
            Count1 =0
            Count2 =0
            flag = False
            if connecTion:
                try:
                    cursor = connecTion.cursor()
                    cursor.execute(SqlSelectQuery)
                    for (val) in cursor:
                        Count1=val
                    cursor.execute(SqlSelectQuery1)
                    for (val) in cursor:
                            Count2=val
                    if Count1[0] == Count2[0]:
                            flag = True
                            cursor.execute(SqlSelectQuery2)
                            for (val) in cursor:
                                returnVal.append(val)
                            cursor.execute(SqlSelectQuery3)
                            for (val) in cursor:
                                returnVal1.append(val)
                    connecTion.commit()
                    cursor.close()  
                    return returnVal,returnVal1,flag
                except Exception as err:
                    cursor.execute(releaseLocks)
                    cursor.close()
                    raise Exception(err)
            else:
                print("300000: Error while connecting to MySql")
                
    def selectRecord(self,value):
        SqlSelectQuery = "select * from CoreCircuitDetails where PatternTag = LTRIM(\'%s\')" %(value)
        connecTion = self.getConnection()
        lockQuery = " LOCK TABLES CoreCircuitDetails READ"
        releaseLocks = " UNLOCK TABLES"
        returnVal = []
        if connecTion:
            try:
                cursor = connecTion.cursor()
                cursor.execute(lockQuery)
                cursor.execute(SqlSelectQuery)
                for (val) in cursor:
                    returnVal.append(val)
                cursor.execute(releaseLocks)
                connecTion.commit()
                cursor.close()
               # if supress == 0:
               # print("Successfully fetched record ")
                return returnVal
            except Exception as err:
                cursor.execute(releaseLocks)
                cursor.close()
                raise Exception(err)
        else:
            print("300000: Error while connecting to MySql")
    
    def selectNodeState(self,value,supress = 0):
                SqlSelectQuery = "select * from nodeState where nodeCommonName = LTRIM(\'%s\')" %(value)
                connecTion = self.getConnection()
                lockQuery = " LOCK TABLES nodeState READ"
                releaseLocks = " UNLOCK TABLES"
                returnVal = []
                if connecTion:
                    try:
                        cursor = connecTion.cursor()
                        if supress == 0:
                            print("Select record : %s",SqlSelectQuery)
                        cursor.execute(lockQuery)
                        cursor.execute(SqlSelectQuery)
                        for (val) in cursor:
                            returnVal.append(val)
                        cursor.execute(releaseLocks)
                        connecTion.commit()
                        return returnVal
                    except Exception as err:
                        cursor.execute(releaseLocks)
                        cursor.close()
                        raise Exception(err)
                else:
                    print("300000: Error while connecting to MySql")    
                    
    def selectCoreRouterDetails(self,value,supress = 0):
        SqlSelectQuery = "select * from CoreCircuitDetails where InternalCircuitID = LTRIM(\'%s\')" %(value)
        connecTion = self.getConnection()
        lockQuery = " LOCK TABLES CoreCircuitDetails READ"
        releaseLocks = " UNLOCK TABLES"
        returnVal = []
        if connecTion:
            try:
                cursor = connecTion.cursor()
                if supress == 0:
                    print("Select record : %s",SqlSelectQuery)
                cursor.execute(lockQuery)
                cursor.execute(SqlSelectQuery)
                for (val) in cursor:
                    returnVal.append(val)
                cursor.execute(releaseLocks)
                connecTion.commit()
                return returnVal
            except Exception as err:
                cursor.execute(releaseLocks)
                cursor.close()
                raise Exception(err)
        else:
            print("300000: Error while connecting to MySql")
     
    def checkInNodeStateTable(self,value):
                SqlSelectQuery = "select count(*) from nodeState where nodeCommonName = LTRIM(\'%s\')" %(value)
                connecTion = self.getConnection()
                lockQuery = " LOCK TABLES  nodeState READ"
                releaseLocks = " UNLOCK TABLES"
                returnVal = 0
                if connecTion:
                    try:
                        cursor = connecTion.cursor()
                        cursor.execute(lockQuery)
                        cursor.execute(SqlSelectQuery)
                        for (val) in cursor:
                            retValue = val
                        cursor.execute(releaseLocks)
                        connecTion.commit()
                        cursor.close()
                        returnVal = retValue[0]   
                        return returnVal
                    except Exception as err:
                        cursor.execute(releaseLocks)
                        cursor.close()
                        raise Exception(err)
                else:
                    print("300000: Error while connecting to MySql")    
                    
    def checkInTable(self,value):
        SqlSelectQuery = "select count(*) from CoreCircuitStates where InternalCircuitID = LTRIM(\'%s\')" %(value)
        connecTion = self.getConnection()
        lockQuery = " LOCK TABLES  CoreCircuitStates READ"
        releaseLocks = " UNLOCK TABLES"
        returnVal = 0
        if connecTion:
            try:
                cursor = connecTion.cursor()
                cursor.execute(lockQuery)
                cursor.execute(SqlSelectQuery)
                for (val) in cursor:
                    retValue = val
                cursor.execute(releaseLocks)
                connecTion.commit()
                cursor.close()
                returnVal = retValue[0]   
                return returnVal
            except Exception as err:
                cursor.execute(releaseLocks)
                cursor.close()
                raise Exception(err)
        else:
            print("300000: Error while connecting to MySql")

    def selectTable(self,tableName,supress = 0):
        SqlSelectQuery = "select * from %s" %(tableName)
        connecTion = self.getConnection()
        lockQuery = " LOCK TABLES %s READ" % (tableName)
        releaseLocks = " UNLOCK TABLES"
        returnVal = []
        if connecTion:
            try:
                cursor = connecTion.cursor()
                cursor.execute(lockQuery)
                cursor.execute(SqlSelectQuery)
                for (val) in cursor:
                    returnVal.append(val)
                cursor.execute(releaseLocks)
                connecTion.commit()
                cursor.close()
                return returnVal
            except Exception as err:
                cursor.execute(releaseLocks)
                cursor.close()
                raise Exception(err)
        else:
            print("300000: Error while connecting to MySql")
            
    def updateNodeStateTable(self,values):
                SqlUpdateQuery = " update nodeState " \
                                 " set Count = LTRIM(\'%s\') , ActualNodes = LTRIM(\'%s\'), flag = LTRIM(\'%s\'), ipaddress = LTRIM(\'%s\') where nodeCommonName = LTRIM(\'%s\')" \
                                 %(values[1],values[2],values[3],values[4],values[0])
                lockQuery = " LOCK TABLES nodeState WRITE"
                releaseLocks = " UNLOCK TABLES"
                connecTion = self.getConnection()
                if connecTion:
                    try:
                        cursor = connecTion.cursor()
                        cursor.execute(lockQuery)
                        cursor.execute(SqlUpdateQuery)
                        cursor.execute(releaseLocks)
                        connecTion.commit()
                        cursor.close()
                    except Exception as e:
                        cursor.execute(releaseLocks)
                        connecTion.commit()
                        cursor.close()
                        print "Error occured during updation",str(e)   
                        
    def updateNodeStateTableAfterMailSend(self,values):
                SqlUpdateQuery = " update nodeState " \
                                 " set flag = LTRIM(\'%s\') where nodeCommonName = LTRIM(\'%s\')" \
                                 %(values[1],values[0])
                lockQuery = " LOCK TABLES nodeState WRITE"
                releaseLocks = " UNLOCK TABLES"
                connecTion = self.getConnection()
                if connecTion:
                    try:
                        cursor = connecTion.cursor()
                        cursor.execute(lockQuery)
                        cursor.execute(SqlUpdateQuery)
                        cursor.execute(releaseLocks)
                        connecTion.commit()
                        cursor.close()
                    except Exception as e:
                        cursor.execute(releaseLocks)
                        connecTion.commit()
                        cursor.close()
                        print "Error occured during updation",str(e)                          
                        
    def updateTable(self,SqlUpdateQuery):
        #SqlUpdateQuery = " update CoreCircuitStates " \
                       #  " set GOCFlag = LTRIM(\'%s\') , Time = LTRIM(\'%s\')  where InternalCircuitID = LTRIM(\'%s\')" \
                        # %(values[1],values[2],values[0])
        lockQuery = " LOCK TABLES CoreCircuitStates WRITE"
        releaseLocks = " UNLOCK TABLES"
        connecTion = self.getConnection()
        if connecTion:
            try:
                cursor = connecTion.cursor()
                cursor.execute(lockQuery)
                cursor.execute(SqlUpdateQuery)
                cursor.execute(releaseLocks)
                connecTion.commit()
                cursor.close()
            except Exception as e:
                cursor.execute(releaseLocks)
                connecTion.commit()
                cursor.close()
                print "Error occured during updation",str(e)
                                                                                
    def deleteRow(self,value):
        SqlDeleteQuery = " delete from CoreCircuitStates where InternalCircuitID = LTRIM(\'%s\')" \
                         %(value)
        lockQuery = " LOCK TABLES CoreCircuitStates WRITE"
        releaseLocks = " UNLOCK TABLES"
        connecTion = self.getConnection()
        if connecTion:
            try:
                cursor = connecTion.cursor()
                cursor.execute(lockQuery)
                cursor.execute(SqlDeleteQuery)
                cursor.execute(releaseLocks)
                connecTion.commit()
                #connecTion.commit()
                cursor.close()
            except Exception as e:
                cursor.execute(releaseLocks)
                connecTion.commit()
                cursor.close()
                print "Error occured during updation",str(e)
                
    def deleteRowInNodeStateTable(self,value):
                    SqlDeleteQuery = " delete from nodeState where nodeCommonName = LTRIM(\'%s\')" \
                                     %(value)
                    lockQuery = " LOCK TABLES nodeState WRITE"
                    releaseLocks = " UNLOCK TABLES"
                    connecTion = self.getConnection()
                    if connecTion:
                        try:
                            cursor = connecTion.cursor()
                            cursor.execute(lockQuery)
                            cursor.execute(SqlDeleteQuery)
                            cursor.execute(releaseLocks)
                            connecTion.commit()
                            #connecTion.commit()
                            cursor.close()
                        except Exception as e:
                            cursor.execute(releaseLocks)
                            connecTion.commit()
                            cursor.close()
                            print "Error occured during updation",str(e)   
        
    def deleteRowNode(self,value):
            SqlDeleteQuery = " delete from nodeState where nodeCommonName = LTRIM(\'%s\')" \
                             %(value)
            lockQuery = " LOCK TABLES nodeState WRITE"
            releaseLocks = " UNLOCK TABLES"
            connecTion = self.getConnection()
            if connecTion:
                try:
                    cursor = connecTion.cursor()
                    cursor.execute(lockQuery)
                    cursor.execute(SqlDeleteQuery)
                    cursor.execute(releaseLocks)
                    connecTion.commit()
                    #connecTion.commit()
                    cursor.close()
                except Exception as e:
                    cursor.execute(releaseLocks)
                    connecTion.commit()
                    cursor.close()
                    print "Error occured during updation",str(e)    
                    
    def deleteRowCCD(self,value):
            SqlDeleteQuery = " delete from CoreCircuitDetails where InternalCircuitID = LTRIM(\'%s\')" \
                             %(value)
            lockQuery = " LOCK TABLES CoreCircuitDetails WRITE"
            releaseLocks = " UNLOCK TABLES"
            connecTion = self.getConnection()
            if connecTion:
                try:
                    cursor = connecTion.cursor()
                    cursor.execute(lockQuery)
                    cursor.execute(SqlDeleteQuery)
                    cursor.execute(releaseLocks)
                    connecTion.commit()
                    #connecTion.commit()
                    cursor.close()
                except Exception as e:
                    cursor.execute(releaseLocks)
                    connecTion.commit()
                    cursor.close()
                    print "Error occured during updation",str(e)   
                                
    def updateSLAState(self,values):
            SqlUpdateQuery = " update CoreCircuitStates " \
                             " set SLAState = LTRIM(\'%s\') , Time = LTRIM(\'%s\') where InternalCircuitID = LTRIM(\'%s\')" \
                             %(values[2],values[1],values[0])
            lockQuery = " LOCK TABLES CoreCircuitStates WRITE"
            releaseLocks = " UNLOCK TABLES"
            connecTion = self.getConnection()
            if connecTion:
                try:
                    cursor = connecTion.cursor()
                    cursor.execute(lockQuery)
                    cursor.execute(SqlUpdateQuery)
                    cursor.execute(releaseLocks)
                    connecTion.commit()
                    #connecTion.commit()
                    cursor.close()
                except Exception as e:
                    cursor.execute(releaseLocks)
                    connecTion.commit()
                    cursor.close()
                    print "Error occured during updation",str(e)
    
    def updateCCD(self,SqlUpdateQuery):
            #SqlUpdateQuery = " update CoreCircuitDetail " \
                           #  " set Time = \'%s\' where InternalCircuitID = \'%s\'" %(values[1],values[0])
            lockQuery = " LOCK TABLES CoreCircuitDetails WRITE"
            releaseLocks = " UNLOCK TABLES"
            connecTion = self.getConnection()
            if connecTion:
                try:
                    cursor = connecTion.cursor()
                    cursor.execute(lockQuery)
                    cursor.execute(SqlUpdateQuery)
                    cursor.execute(releaseLocks)
                    connecTion.commit()
                    #connecTion.commit()
                    cursor.close()
                except Exception as e:
                    cursor.execute(releaseLocks)
                    connecTion.commit()
                    cursor.close()
                    print "Error occured during updation",str(e)                        
                    
    def updateTime(self,values):
            SqlUpdateQuery = " update CoreCircuitStates " \
                             " set Time = LTRIM(\'%s\') where InternalCircuitID = LTRIM(\'%s\')" %(values[1],values[0])
            lockQuery = " LOCK TABLES CoreCircuitStates WRITE"
            releaseLocks = " UNLOCK TABLES"
            connecTion = self.getConnection()
            if connecTion:
                try:
                    cursor = connecTion.cursor()
                    cursor.execute(lockQuery)
                    cursor.execute(SqlUpdateQuery)
                    cursor.execute(releaseLocks)
                    connecTion.commit()
                    #connecTion.commit()
                    cursor.close()
                except Exception as e:
                    cursor.execute(releaseLocks)
                    connecTion.commit()
                    cursor.close()
                    print "Error occured during updation",str(e)
                    
    def updateColumn(self,tableName,columName,Value,conditionField,condValue):
            returnValue=-1
            SqlUpdateQuery = " update  %s " \
                             " set %s = \'%s\' where %s = \'%s \'" %(tableName,columName,Value,conditionField,condValue)
    
            lockQuery = " LOCK TABLES %s WRITE" % (tableName)
            releaseLocks = " UNLOCK TABLES"
            connecTion = self.getConnection()
            if  connecTion:
                try:
                    cursor = connecTion.cursor()
                    log.info("600010: Updating record : %s",SqlUpdateQuery)
                    log.info("600010: updating {} %s in table %s {}: ",columName,tableName)
                    cursor.execute(lockQuery)
                    cursor.execute(SqlUpdateQuery)
                    cursor.execute(releaseLocks)
                    connecTion.commit()
                    cursor.close()
                    log.info("600000: Record updated ")
                    returnValue=1
                except mysql.connector.Error as err:
                    print err
                    cursor.execute(releaseLocks)
                    connecTion.commit()
                    cursor.close()
                    raise Exception(err)
            return returnValue


                                                                                    
                                






