
import os.path
import sys
file_path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.path.pardir))
if file_path not in sys.path:
    sys.path.insert(0, file_path) 
import requests
import json
import base64

class Orion:

    def __init__(self,username,password,Nodename):
	    self.baseUrl = "https://ops.emc-corp.net:17778/SolarWinds/InformationService/v3/Json/Query?query=SELECT+n.Caption+,+n.IPAddress+,+n.CustomProperties.City+,+n.CustomProperties.Customer+,+n.CustomProperties.Country+FROM+Orion.Nodes+n+WHERE+Caption+=+\'"+Nodename+"\'"
	    self.credentials = (username, password)

    def _req(self):
	    return requests.request("GET",self.baseUrl,
	                          verify = False,
	                          auth = self.credentials,
	                          headers = {'Content-Type' : 'application/json'})
    def  query(self):
	    return self._req()
	
if __name__== "__main__":
	swis = Orion('svcorionnet@emc-corp.net',base64.b64decode("JFYoMHIhME4zdA=="),'EMC_RAI_3825_1_SERV')    
	out=swis.query().json()
	list=out['results']
	print out
	for i in list:
	      print "Node Name : "+i['Caption']+" IP Address :"+i['IPAddress']+" CIty"+i['City']


