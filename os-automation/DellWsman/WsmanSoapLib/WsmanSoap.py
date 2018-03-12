# -*- coding: cp1252 -*-
import urllib2
import httplib
import XMLChef as chef
from XMLChef import getAVMapFromXMLFile, createXMLFileFromAVMap
import os
import datetime,ssl
import sys
import time
current_time = lambda: int(round(time.time())*1000)

# This disables all certificate verification for version 2.7.9 and above
if sys.hexversion >= 34015728:
    ssl._create_default_https_context = ssl._create_unverified_context

class WsmanSoap():
    def __init__(self,ip,user,pwd,maxBatchItems=256,maxTimeout=120000,maxEnvelope=200,optimize=True,port=443):
        self.ip=ip
        self.port=port
        self.user=user
        self.pwd=pwd
        self.maxBatchItems=str(maxBatchItems)
        self.maxTimeout=str(maxTimeout)
        self.maxEnvelope=str(int(maxEnvelope)*1024)
        self.optimize=optimize

        self.xmlCook=chef.XMLChef('https://' + self.ip + ':%s/wsman'%self.port,self.maxBatchItems,self.maxTimeout,self.maxEnvelope,self.optimize)
        

        auth_handler = urllib2.HTTPBasicAuthHandler()
        auth_handler.add_password(realm='OPENWSMAN',
                          uri='https://' + self.ip + ':%s/wsman'%self.port,
                          user=self.user,
                          passwd=self.pwd)
        self.opener = urllib2.build_opener(auth_handler)
        #urllib2.install_opener(opener)

    def debugXML(self,reqXmlStr=""):
        '''Send any text data to the WSMan Server'''
        try:
            responseXmlStr, timeTaken=self.send(reqXmlStr,True)
            returnContentStr, nItems, Fault = chef.getItemsFromXmlStr(responseXmlStr)            
            return reqXmlStr,responseXmlStr, returnContentStr, Fault, timeTaken
        except:
            return "","","",1,0

    def identify(self):
        '''WSMan Identify, used to identify the service'''
        reqXmlStr=chef.getIdentifyXmlStr()
        try:
            responseXmlStr, timeTaken=self.send(reqXmlStr,True)
            returnContentStr, nItems, Fault = chef.getItemsFromXmlStr(responseXmlStr)            
            return reqXmlStr,responseXmlStr, returnContentStr, Fault, timeTaken
        except:
            return "","","",1,0

    def getEPR(self,cimns,resourceURI):
        '''Enumerate End Point References'''
        return self.enum(cimns,resourceURI,fragmentname='',filters=[],dialect=None,typ='epr')

    def subscribe(self,subscriptionClass,cimns,replyURL,heartBeat,expiry,jid=None):
        '''Subscribe to a Events covered by a specific Class'''
        actionURI='http://schemas.xmlsoap.org/ws/2004/08/eventing/Subscribe'
        resourceURI='http://schemas.dmtf.org/wbem/wscim/1/*'

        filterStr='SELECT * FROM ' + subscriptionClass

        if jid:
            filterStr+=' WHERE JOB_ID='+jid

        reqXmlStr = self.xmlCook.getSubscribeXmlStr(resourceURI,actionURI,cimns,filterStr,replyURL,heartBeat,expiry)
        
        responseXmlStr, timeTaken = self.send(reqXmlStr, True)
        returnContentStr, nItems, Fault = chef.getItemsFromXmlStr(responseXmlStr)

        return reqXmlStr, responseXmlStr, returnContentStr, Fault, timeTaken

    def unsubscribe(self,identifier,cimns):
        '''Unsubscribe from events identified by a particular subscription ID'''
        actionURI='http://schemas.xmlsoap.org/ws/2004/08/eventing/Unsubscribe'

        reqXmlStr = self.xmlCook.getUnsubscribeXmlStr(actionURI,cimns,identifier)

        responseXmlStr, timeTaken = self.send(reqXmlStr, True)

        returnContentStr, nItems, Fault = chef.getItemsFromXmlStr(responseXmlStr)

        return reqXmlStr, responseXmlStr, returnContentStr, Fault, timeTaken

    def renewSubscription(self,identifier,expires,cimns):
        '''Renew a particular subscription identified by it's subscription ID'''
        actionURI='http://schemas.xmlsoap.org/ws/2004/08/eventing/Renew'

        reqXmlStr = self.xmlCook.getRenewSubscriptionXmlStr(actionURI,cimns,identifier,expires)

        responseXmlStr, timeTaken = self.send(reqXmlStr, True)

        returnContentStr, nItems, Fault = chef.getItemsFromXmlStr(responseXmlStr)

        return reqXmlStr, responseXmlStr, returnContentStr, Fault, timeTaken

        

    def invoke(self,resourceURI,selectorSetStr,method,attributeValueMaporFilename):
        '''Invoke a particular method of a class instance identified by it's selector set'''
        if type(attributeValueMaporFilename) is dict:
            attributeValueMap=attributeValueMaporFilename
        else:
            fileName=attributeValueMaporFilename
            attributeValueMap = getAVMapFromXMLFile(fileName)
        
        returnXmlStr = ""
        returnContentStr = ""
        actionURI=resourceURI+'/'+method

        reqXmlStr = self.xmlCook.getInvokeXmlStr(resourceURI,actionURI,selectorSetStr,method,attributeValueMap)

        responseXmlStr, timeTaken = self.send(reqXmlStr, True)
        returnContentStr, nItems, Fault = chef.getItemsFromXmlStr(responseXmlStr)
        
        return reqXmlStr, responseXmlStr, returnContentStr, Fault, timeTaken

    def Set(self,resourceURI,selectorSetStr,attributeValueMaporFilename):
        '''Set property of an instance of a class identified by it's selector set'''
        rxml, getResponseXml, getContentStr, Fault, timeTaken = self.get(resourceURI,selectorSetStr,'')

        resourceURI=resourceURI.replace('dell.com','dmtf.org')

        if type(attributeValueMaporFilename) is dict:
            attributeValueMap=attributeValueMaporFilename
        else:
            fileName=attributeValueMaporFilename
            attributeValueMap = getAVMapFromXMLFile(fileName)

        returnXmlStr = ""
        returnContentStr = ""
        actionURI=u'http://schemas.xmlsoap.org/ws/2004/09/transfer/Put'

        reqXmlStr = self.xmlCook.getSetXmlStr(resourceURI,actionURI,selectorSetStr,attributeValueMap,getResponseXml)

        responseXmlStr, timeTaken = self.send(reqXmlStr, True)
        returnContentStr, nItems, Fault = chef.getItemsFromXmlStr(responseXmlStr)
        return reqXmlStr, responseXmlStr, returnContentStr, Fault, timeTaken

            

    def get(self,resourceURI,selectorSetStr,fragmentname=''):
        '''Get an instance of a class identified by it's selector set'''
        returnXmlStr = ""
        returnContentStr = ""
        actionURI=u'http://schemas.xmlsoap.org/ws/2004/09/transfer/Get'

        reqXmlStr = self.xmlCook.getGetXmlStr(resourceURI,actionURI,selectorSetStr,fragmentname)
            
        responseXmlStr, timeTaken = self.send(reqXmlStr, True)

        returnContentStr, nItems, Fault = chef.getItemsFromXmlStr(responseXmlStr)
        
        return reqXmlStr, responseXmlStr, returnContentStr, Fault, timeTaken

    '''def generateCompactSelectorSetsMap(self,selectorSetsXML):
        try:
            selectorSetsList=[]
            for selectorSetXML in selectorSetsXML:
                selectorSet = chef.getSelectors(selectorSetXML)
                print "$$$$$ %s" %selectorSet
                selectorSetsList.append(selectorSet)    
                

            ##check for uniqueness
            
            numSelectors = len(selectorSetsList[0])

            j=0
            while j < numSelectors:
                t=[]
                for i in range(0,len(selectorSetsList)):
                    t.append(selectorSetsList[i][j])
                if len(set(t))==1 and len(t)>1:
                    for ii in range(0,len(selectorSetsList)):
                        selectorSetsList[ii].remove(t[0])
                    numSelectors-=1
                else:
                    j+=1

            i=0
            selectorSetsMap={}
            while i < len(selectorSetsList):
                selectorSetString=''
                for selector in selectorSetsList[i]:
                    selectorSetString += selector + "; "  
                selectorSetsMap[selectorSetString]=str(selectorSetsXML[i])
                i=i+1
            return selectorSetsMap
        except:
            return {}'''
            
        

    def getSelectorSets(self,cimns,resourceURI,caller='GET'):
        '''Get the selector sets as a list to work with GETs'''
        selectorSets = []
        actionURI=u'http://schemas.xmlsoap.org/ws/2004/09/enumeration/Enumerate'
        destURI=u'https://' + self.ip + u':%s/wsman'%self.port

        reqXmlStr = self.xmlCook.getEnumXmlStr(resourceURI,actionURI,cimns,'epr','','')

        responseXmlStr, timeTaken = self.send(reqXmlStr, True)

        try:
            selectorSets+=chef.extractSelectorsFromXML(responseXmlStr)
            enumContext,endOfSequence=self.xmlCook.getEnumerationContext(responseXmlStr)
            while enumContext and not endOfSequence:
                reqXmlStr = self.xmlCook.getEnumPullXmlStr(enumContext,resourceURI,'http://schemas.xmlsoap.org/ws/2004/09/enumeration/Pull',cimns,'epr','')
                responseXmlStr, timeTaken = self.send(reqXmlStr)
                enumContext,endOfSequence=self.xmlCook.getEnumerationContext(responseXmlStr)
                selectorSets+=chef.extractSelectorsFromXML(responseXmlStr)
        except Exception as e:
            print e
            if caller=='GET':
                return {}
            else:
                return []

        if caller == 'association' or caller == 'references':
            filterXMLs=[]
            for selSet in selectorSets:
                filterXMLs.append(chef.getFilterXml('http://schemas.dmtf.org/wbem/wsman/1/cimbinding/associationFilter',resourceURI,selSet,caller))
            return filterXMLs
        #CompactSelectorSetsMap=self.generateCompactSelectorSetsMap(selectorSets)
        #return CompactSelectorSetsMap
        return selectorSets


    def associations(self,cimns,resourceURI,typ):
        '''Get all associations/references of the specified Class'''
        allResponseXmlStrs = ""
        allReqXmlStrs = ""
        returnContentStr = ""
        Fault=True
        actionURI=u'http://schemas.xmlsoap.org/ws/2004/09/enumeration/Enumerate'
        nItems=0
        totalItems=0
        
        filterXMLs=self.getSelectorSets(cimns,resourceURI,typ)
        #print filterXMLs
        totalTimeTaken=0.0
        for filterXML in filterXMLs:
            reqXmlStr = self.xmlCook.getEnumXmlStr(resourceURI,actionURI,cimns,'','',filterXML)
            allReqXmlStrs += reqXmlStr + "\n\n"
            responseXmlStr, timeTaken = self.send(reqXmlStr, True)
            totalTimeTaken+=timeTaken
            responseContentStr, nItems, Fault = chef.getItemsFromXmlStr(responseXmlStr)
            totalItems+=nItems
            
            allResponseXmlStrs += responseXmlStr + "\n\n"
            returnContentStr += responseContentStr

            enumContext,endOfSequence=self.xmlCook.getEnumerationContext(responseXmlStr)
            
            while enumContext and not endOfSequence and not Fault:
                reqXmlStr = self.xmlCook.getEnumPullXmlStr(enumContext,resourceURI,'http://schemas.xmlsoap.org/ws/2004/09/enumeration/Pull',cimns,fragmentname)
                allReqXmlStrs += reqXmlStr + "\n\n"
                responseXmlStr, timeTaken = self.send(reqXmlStr)
                totalTimeTaken+=timeTaken
                responseContentStr, nItems, Fault = chef.getItemsFromXmlStr(responseXmlStr)
                totalItems+=nItems
                
                
                allResponseXmlStrs += responseXmlStr + "\n\n"
                returnContentStr += responseContentStr

                enumContext,endOfSequence=self.xmlCook.getEnumerationContext(responseXmlStr)
                
        if not len(filterXMLs):
            Fault=False
        
        return allReqXmlStrs, allResponseXmlStrs, returnContentStr, Fault, totalTimeTaken, totalItems
        

    def enum(self,cimns,resourceURI,fragmentname='',filters=[],dialect=None,typ=''):
        '''Enumerate a Class'''
        enumType = 'epr' if typ == 'epr' else ''
        totalTimeTaken=0.0
        
        allResponseXmlStrs = ""
        allReqXmlStrs = ""
        returnContentStr = ""
        actionURI=u'http://schemas.xmlsoap.org/ws/2004/09/enumeration/Enumerate'
        destURI=u'https://' + self.ip + u':%s/wsman'%self.port
        nItems=0
        totalItems=0
        
        filterXML=None
        
        
        if len(filters):
            if not dialect:
                dialect="http://schemas.dmtf.org/wbem/cql/1/dsp0202.pdf"
            classname = resourceURI.split('/')[-1].strip()
            filterXML=chef.getFilterXMLfromSQL(filters,dialect,classname)
            
        reqXmlStr=self.xmlCook.getEnumXmlStr(resourceURI,actionURI,cimns,enumType,fragmentname,filterXML)
        allReqXmlStrs += reqXmlStr + "\n\n"
        responseXmlStr, timeTaken = self.send(reqXmlStr, True)
        totalTimeTaken+=timeTaken
        responseContentStr, nItems, Fault = chef.getItemsFromXmlStr(responseXmlStr)
        totalItems+=nItems
        
        allResponseXmlStrs += responseXmlStr + "\n\n"
        returnContentStr += responseContentStr

        enumContext,endOfSequence=self.xmlCook.getEnumerationContext(responseXmlStr)
        
        while enumContext and not endOfSequence and not Fault:
            try:
                reqXmlStr = self.xmlCook.getEnumPullXmlStr(enumContext,resourceURI,'http://schemas.xmlsoap.org/ws/2004/09/enumeration/Pull',cimns,enumType,fragmentname)
                allReqXmlStrs += reqXmlStr + "\n\n"
                responseXmlStr, timeTaken = self.send(reqXmlStr)
                totalTimeTaken+=timeTaken
                responseContentStr, nItems, Fault = chef.getItemsFromXmlStr(responseXmlStr)
                totalItems+=nItems

                allResponseXmlStrs += responseXmlStr+ "\n\n"
                returnContentStr += responseContentStr

                enumContext,endOfSequence=self.xmlCook.getEnumerationContext(responseXmlStr)
            except:
                break

        return allReqXmlStrs, allResponseXmlStrs, returnContentStr, Fault, totalTimeTaken, totalItems

    def send(self, data, authRequired=False):
        '''Send the XML to the WSMan Server'''
        def cleanXML(xmlStr):
            cleanXmlStr=xmlStr
            for ch in xmlStr:
                order=ord(ch)
                if order > 127 or (order < 20 and order != 10):
                    cleanXmlStr=cleanXmlStr.replace(ch,'\\x%d' %order)
            return cleanXmlStr
                    
        reqID=str(time.time()).replace('.','')
        
        headers = {
		'Host': self.ip,
		'Accept': '*/*',
		'Content-Type': 'application/soap+xml;charset=utf-8',
		'User-Agent': 'WSMAN-Console',
		'Content-Length': len(data),
		'Expect': '100-continue'
        }
        '''site = 'https://' + self.ip + ':443/wsman'

        if authRequired:
            auth_handler = urllib2.HTTPBasicAuthHandler()
            auth_handler.add_password(realm='OPENWSMAN',
                              uri=site,
                              user=self.user,
                              passwd=self.pwd)
            opener = urllib2.build_opener(auth_handler)
            urllib2.install_opener(opener)
        req = urllib2.Request(site, data, headers)
        req.get_method = lambda: 'POST'
        timeTaken=0'''
        site = 'https://' + self.ip + ':%d/wsman'%self.port
        try:
            req = urllib2.Request(site, data, headers)
        except Exception as e:
            print e

        req.get_method = lambda: 'POST'
        try:
            endTime=startTime=datetime.datetime.now()
            #response = urllib2.urlopen(req,timeout=((int)(self.maxTimeout)/1000)+30)#,context=ssl.SSLContext(ssl.PROTOCOL_TLSv1))
            response = self.opener.open(req,timeout=((int)(self.maxTimeout)/1000)+30)#,context=ssl.SSLContext(ssl.PROTOCOL_TLSv1))
            responseXmlStr=cleanXML(response.read())
        except urllib2.HTTPError, e:
            responseXmlStr = chef.getExceptionXml('HTTP EXCEPTION','There was an HTTP Error',e)
        except urllib2.URLError, e:
            responseXmlStr = chef.getExceptionXml('HTTP','There was a URL Error',e)
        except IOError, e:
            responseXmlStr = chef.getExceptionXml('HTTP','There was an IO Error',e)
        except httplib.BadStatusLine, e:
            responseXmlStr = chef.getExceptionXml('HTTP','There was a BadStatusLine Error',e)
        except Exception as e:
            responseXmlStr = chef.getExceptionXml('HTTP','There was an unknown Exception',e)
        finally:
            endTime=datetime.datetime.now()
            timeTaken=(endTime-startTime).total_seconds()

        return responseXmlStr, timeTaken

#Testing Module

if __name__ == "__main__":
    def parse(data):
#        print data
        if data[3] == False:
            return "Got Response in %f seconds\n%s" %(data[4],data[2])
        else:
            return "Failed in %f seconds\n%s" %(data[4],data[2])
    soaplib = WsmanSoap(ip='10.94.225.90',
                        user='root',
                        pwd='calvin',
                        maxBatchItems=256,
                        maxTimeout=90000,
                        maxEnvelope=500,
                        optimize=True)

    print "Checking Identify: ", 
    print parse(soaplib.identify())

    print "Checking Enum: ",
    print parse(soaplib.enum('root/dcim','http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/DCIM_iDRACCardView'))

    print "Checking Get: ",
    print parse(soaplib.get('http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/DCIM_iDRACCardEnumeration',
                            '<wsman:SelectorSet xmlns:wsman="http://schemas.dmtf.org/wbem/wsman/1/wsman.xsd"><wsman:Selector Name="__cimnamespace">root/dcim</wsman:Selector><wsman:Selector Name="InstanceID">iDRAC.Embedded.1#AutoOSLockGroup.1#AutoOSLockState</wsman:Selector></wsman:SelectorSet>'))

    print "Checking Invoke: ",
    print parse(soaplib.invoke('http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/DCIM_LCService',
                               '<wsman:SelectorSet xmlns:wsman="http://schemas.dmtf.org/wbem/wsman/1/wsman.xsd"><wsman:Selector Name="__cimnamespace">root/dcim</wsman:Selector><wsman:Selector Name="SystemCreationClassName">DCIM_ComputerSystem</wsman:Selector><wsman:Selector Name="SystemName">DCIM:ComputerSystem</wsman:Selector><wsman:Selector Name="CreationClassName">DCIM_LCService</wsman:Selector><wsman:Selector Name="Name">DCIM:LCService</wsman:Selector></wsman:SelectorSet>',
                               'ExportLCLog',
                               {'Username': 'bfgfgb', 'Workgroup': 'bfgdf', 'ShareType': '2', 'ShareName': 'bf', 'FileName': 'bgdgbdfb', 'Password': 'hrtdhe', 'IPAddress': '10.94.225.250'}))
    
    
