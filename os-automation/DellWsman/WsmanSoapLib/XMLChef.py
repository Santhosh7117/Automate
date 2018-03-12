import xml.etree.ElementTree as ET
import copy
from xml.etree.ElementTree import dump
import uuid
class XMLChef():
    def __init__(self,destURI,maxBatchItems,maxTimeout,maxEnvelope,optimize):
        ET.register_namespace("s","http://www.w3.org/2003/05/soap-envelope")
        ET.register_namespace("wsa","http://schemas.xmlsoap.org/ws/2004/08/addressing")
        ET.register_namespace("wsman","http://schemas.dmtf.org/wbem/wsman/1/wsman.xsd")
        ET.register_namespace("wsen","http://schemas.xmlsoap.org/ws/2004/09/enumeration")
        ET.register_namespace('wse',"http://schemas.xmlsoap.org/ws/2004/08/eventing")

        self.namespaces={"s":"http://www.w3.org/2003/05/soap-envelope",
                    "wsa":"http://schemas.xmlsoap.org/ws/2004/08/addressing",
                    "wsman":"http://schemas.dmtf.org/wbem/wsman/1/wsman.xsd",
                    "wsen":"http://schemas.xmlsoap.org/ws/2004/09/enumeration",
                    "wse":"http://schemas.xmlsoap.org/ws/2004/08/eventing"}

        self.setHeader(destURI,maxTimeout,maxEnvelope,optimize)

        self.maxBatchItems=maxBatchItems
        self.optimize=optimize

    def setHeader(self,destURI,maxTimeout,maxEnvelope,optimize):
        xmlStr="""<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope" xmlns:wsa="http://schemas.xmlsoap.org/ws/2004/08/addressing" xmlns:wsman="http://schemas.dmtf.org/wbem/wsman/1/wsman.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<s:Header>
<wsa:To s:mustUnderstand="true">vsdvsdv</wsa:To>
<wsman:ResourceURI s:mustUnderstand="true"></wsman:ResourceURI>
<wsa:ReplyTo><wsa:Address s:mustUnderstand="true">http://schemas.xmlsoap.org/ws/2004/08/addressing/role/anonymous</wsa:Address></wsa:ReplyTo>
<wsa:Action s:mustUnderstand="true"></wsa:Action>
<wsman:MaxEnvelopeSize s:mustUnderstand="true"></wsman:MaxEnvelopeSize>
<wsa:MessageID s:mustUnderstand="true"></wsa:MessageID>
<wsman:OperationTimeout></wsman:OperationTimeout>
</s:Header>
<s:Body/>
</s:Envelope>"""
        self.root=ET.fromstring(xmlStr)
        header=self.root.find('s:Header',namespaces=self.namespaces)
        
        header.find('wsa:To',namespaces=self.namespaces).text=destURI
        
        t=int(maxTimeout)
        timeoutStr = "PT" + str(t/1000) + "." + str(t%1000) + "S"
        header.find('wsman:OperationTimeout',namespaces=self.namespaces).text=timeoutStr

        header.find('wsman:MaxEnvelopeSize',namespaces=self.namespaces).text=maxEnvelope

    def setResourceAndActionURI(self,xml,resourceURI,actionURI):
        header=xml.find('s:Header',namespaces=self.namespaces)
        if resourceURI:
            header.find('wsman:ResourceURI',namespaces=self.namespaces).text=resourceURI
        else:
            #print dir(header)
            #print help(header.remove)
            #print dir(header.remove)
            header.remove(header.find('wsman:ResourceURI',namespaces=self.namespaces))
        
        header.find('wsa:Action',namespaces=self.namespaces).text=actionURI
        header.find('wsa:MessageID',namespaces=self.namespaces).text=uuid.uuid1().urn
        return xml

    def setCimns(self,xml,cimns):
        header=xml.find('s:Header',namespaces=self.namespaces)
        selectorsetTag=ET.SubElement(header,"wsman:SelectorSet")
        #selectorsetTag=header.find('wsman:SelectorSet',namespaces=self.namespaces)
        selTag=ET.SubElement(selectorsetTag,"wsman:Selector")
        selTag.attrib["Name"]="__cimnamespace"
        selTag.text=cimns
        return xml

    def setSelectorSet(self,xml,selectorSet):
        resURI=''
        header=xml.find('s:Header',namespaces=self.namespaces)
        #selectorsetTag=header.find('wsman:SelectorSet',namespaces=self.namespaces)
        #index=selectorSet.find('>')
        #selectorSet = selectorSet[:index] + ' xmlns:wsman="http://schemas.dmtf.org/wbem/wsman/1/wsman.xsd"' + selectorSet[index:]
        ReferenceParametersTag=ET.fromstring(selectorSet)
        for child in ReferenceParametersTag:
            if child.tag.endswith('ResourceURI'):
                resURI = child.text
            elif child.tag.endswith('SelectorSet'):
                header.append(child)
        #print "****"
        #print ET.tostring(xml)
        #print resURI
        #print "****"
        return xml, resURI     
        

    def getEnumXmlStr(self,resourceURI,actionURI,cimns,enumerationMode,fragmentName,filterXMLStr=None):
        xml=copy.deepcopy(self.root)
        xml.attrib['xmlns:wsen']="http://schemas.xmlsoap.org/ws/2004/09/enumeration"
        
        xml = self.setResourceAndActionURI(xml,resourceURI,actionURI)

        header=xml.find('s:Header',namespaces=self.namespaces)

        xml=self.setCimns(xml,cimns)

        if fragmentName:
            tag=ET.SubElement(header,"wsman:FragmentTransfer")
            tag.attrib["s:mustUnderstand"]="true"
            tag.text=fragmentName

        body=xml.find('s:Body',namespaces=self.namespaces)

        enumTag=ET.SubElement(body,"wsen:Enumerate")

        if(self.optimize):
            ET.SubElement(enumTag,"wsman:OptimizeEnumeration")
        if enumerationMode == 'epr':
            tag=ET.SubElement(enumTag,"wsman:EnumerationMode")
            tag.text="EnumerateEPR"
        tag=ET.SubElement(enumTag,"wsman:MaxElements")
        tag.text=self.maxBatchItems

        if filterXMLStr:
            filterXmlTag=ET.fromstring(filterXMLStr)
            enumTag.append(filterXmlTag)

        return ET.tostring(xml,encoding="UTF-8",method="xml")

    def getEnumPullXmlStr(self,enumContext,resourceURI,actionURI,cimns,enumerationMode,fragmentName):
        xml=copy.deepcopy(self.root)
        xml.attrib['xmlns:wsen']="http://schemas.xmlsoap.org/ws/2004/09/enumeration"
        
        xml = self.setResourceAndActionURI(xml,resourceURI,actionURI)

        header=xml.find('s:Header',namespaces=self.namespaces)

        if fragmentName:
            tag=ET.SubElement(header,"wsman:FragmentTransfer")
            tag.attrib["s:mustUnderstand"]="true"
            tag.text=fragmentName

        xml=self.setCimns(xml,cimns)

        body=xml.find('s:Body',namespaces=self.namespaces)

        pullTag=ET.SubElement(body,"wsen:Pull")
        if enumerationMode == 'epr':
            tag=ET.SubElement(pullTag,"wsman:EnumerationMode")
            tag.text="EnumerateEPR"
        tag=ET.SubElement(pullTag,"wsen:EnumerationContext")
        tag.text=str(enumContext)
        tag=ET.SubElement(pullTag,"wsman:MaxElements")
        tag.text=self.maxBatchItems

        return ET.tostring(xml,encoding="UTF-8",method="xml")


    def getGetXmlStr(self,resourceURI,actionURI,selectorSet,fragmentName):
        xml=copy.deepcopy(self.root)
        #xml = self.setResourceAndActionURI(xml,resourceURI,actionURI)

        header=xml.find('s:Header',namespaces=self.namespaces)

        xml,resURI=self.setSelectorSet(xml,selectorSet)
        xml = self.setResourceAndActionURI(xml,resURI,actionURI)
        if fragmentName:
            tag=ET.SubElement(header,"wsman:FragmentTransfer")
            tag.attrib["s:mustUnderstand"]="true"
            tag.text=fragmentName

        return ET.tostring(xml,encoding="UTF-8",method="xml")

    def getInvokeXmlStr(self,resourceURI,actionURI,selectorSet,methodName,attributeValueMap):
        xml=copy.deepcopy(self.root)

        xml = self.setResourceAndActionURI(xml,resourceURI,actionURI)

        header=xml.find('s:Header',namespaces=self.namespaces)

        xml,resURI=self.setSelectorSet(xml,selectorSet)

        newNamespace=("n1",resourceURI)
        
        self.namespaces[newNamespace[0]]=newNamespace[1]
        ET.register_namespace(newNamespace[0],newNamespace[1])
        bodyXmlStr='<s:Body xmlns:s="%s" xmlns:%s="%s"></s:Body>'%(self.namespaces['s'],newNamespace[0],newNamespace[1])
        newBodyTag=ET.fromstring(bodyXmlStr)
        methodTag=ET.SubElement(newBodyTag,"n1:%s_INPUT"%(methodName))
        for attribute in attributeValueMap.keys():
            if attributeValueMap[attribute] == None:
                continue
            for value in str(attributeValueMap[attribute]).split(','):
                value=value.strip()
                tag=ET.SubElement(methodTag,"n1:%s"%(attribute))
                tag.text=value

        body=xml.find('s:Body',namespaces=self.namespaces)
        body.extend(newBodyTag)
        xml.attrib["xmlns:%s"%(newNamespace[0])]=newNamespace[1]
        return ET.tostring(xml,encoding="UTF-8",method="xml")


    def getSetXmlStr(self,resourceURI,actionURI,selectorSet,attributeValueMap,getResponseXmlStr):
        xml=copy.deepcopy(self.root)
        xml = self.setResourceAndActionURI(xml,resourceURI,actionURI)

        header=xml.find('s:Header',namespaces=self.namespaces)

        xml,resURI=self.setSelectorSet(xml,selectorSet)

        ET.register_namespace('n1',resourceURI)

        respXml=ET.fromstring(getResponseXmlStr.replace("dell.com","dmtf.org"))

        
        mynamespaces=copy.deepcopy(self.namespaces)
        mynamespaces['n1']=resourceURI

        
        respXml.find('s:Header',namespaces=mynamespaces).clear()
        '''respHeader.remove(respHeader.find('wsa:To',namespaces=mynamespaces))
        respHeader.remove(respHeader.find('wsa:Action',namespaces=mynamespaces))
        respHeader.remove(respHeader.find('wsa:RelatesTo',namespaces=mynamespaces))
        respHeader.remove(respHeader.find('wsa:MessageID',namespaces=mynamespaces))'''
        respXml.find('s:Header',namespaces=mynamespaces).extend(header)
        xml=respXml
    
        
        body=xml.find('s:Body',namespaces=mynamespaces)
        className = resourceURI.split('/')[-1].strip()
        data=body.find('n1:%s'%className,namespaces=mynamespaces)

        for attribute in attributeValueMap.keys():
            try:
                data.find('n1:%s'%attribute,namespaces=mynamespaces).text=attributeValueMap[attribute]
            except:
                pass

        return ET.tostring(xml,encoding="UTF-8",method="xml")

    def getSubscribeXmlStr(self,resourceURI,actionURI,cimns,filterStr,replyURL,heartBeat,expiry):
        xml=copy.deepcopy(self.root)

        xml = self.setResourceAndActionURI(xml,resourceURI,actionURI)

        header=xml.find('s:Header',namespaces=self.namespaces)

        xml=self.setCimns(xml,cimns)
        
        body=xml.find('s:Body',namespaces=self.namespaces)
        
        subscribeTag=ET.SubElement(body,'wse:Subscribe')
        deliveryTag=ET.SubElement(subscribeTag,'wse:Delivery')
        deliveryTag.attrib['Mode']="http://schemas.xmlsoap.org/ws/2004/08/eventing/DeliveryModes/Push"
        tag=ET.SubElement(deliveryTag,'wse:NotifyTo')
        subtag=ET.SubElement(tag,'wsa:Address')
        subtag.text=replyURL
        if heartBeat:
            tag=ET.SubElement(deliveryTag,"wsman:Heartbeats")
            tag.text="PT%s.0S"%heartBeat
        elif expiry:
            tag=ET.SubElement(subscribeTag,"wse:Expires")
            tag.text="PT%s.0S"%expiry

        tag=ET.SubElement(subscribeTag,'wsman:Filter')
        tag.attrib['Dialect']="http://schemas.microsoft.com/wbem/wsman/1/WQL"
        tag.text=filterStr
        xml.attrib['xmlns:wse']="http://schemas.xmlsoap.org/ws/2004/08/eventing"
        
        return ET.tostring(xml,encoding="UTF-8",method="xml")

    def getUnsubscribeXmlStr(self,actionURI,cimns,identifier):
        xml=copy.deepcopy(self.root)
        xml = self.setResourceAndActionURI(xml,'',actionURI)

        header=xml.find('s:Header',namespaces=self.namespaces)

        IdentifierTag = ET.SubElement(header,'wse:Identifier')
        IdentifierTag.text=identifier

        xml=self.setCimns(xml,cimns)
        
        body=xml.find('s:Body',namespaces=self.namespaces)
        ET.SubElement(body,'wse:Unsubscribe')

        xml.attrib['xmlns:wse']="http://schemas.xmlsoap.org/ws/2004/08/eventing"
        
        return ET.tostring(xml,encoding="UTF-8",method="xml")

    def getRenewSubscriptionXmlStr(self,actionURI,cimns,identifier,expires):
        xml=copy.deepcopy(self.root)
        xml = self.setResourceAndActionURI(xml,'',actionURI)

        header=xml.find('s:Header',namespaces=self.namespaces)

        IdentifierTag = ET.SubElement(header,'wse:Identifier')
        IdentifierTag.text=identifier

        xml=self.setCimns(xml,cimns)
        
        body=xml.find('s:Body',namespaces=self.namespaces)
        renewTag = ET.SubElement(body,'wse:Renew')

        expiresTag = ET.SubElement(renewTag,'wse:Expires')
        expiresTag.text = "PT%s.0S"%expires

        xml.attrib['xmlns:wse']="http://schemas.xmlsoap.org/ws/2004/08/eventing"
        
        return ET.tostring(xml,encoding="UTF-8",method="xml")

    def getEnumerationContext(self,xmlStr):
        if not xmlStr:
            return None,None
        xml=ET.fromstring(xmlStr)
        bodyTag=xml.find('s:Body',namespaces=self.namespaces)
        if bodyTag is not None:
            ERTag=bodyTag.find('wsen:EnumerateResponse',namespaces=self.namespaces)
            if ERTag is None:
                ERTag=bodyTag.find('wsen:PullResponse',namespaces=self.namespaces)
            if ERTag is not None:
                ECTag=ERTag.find('wsen:EnumerationContext',namespaces=self.namespaces)
                if ECTag is not None:
                    return ECTag.text, False
                EOSTag=ERTag.find('wsen:EndOfSequence',namespaces=self.namespaces)
                if EOSTag is not None:
                    return None, True
        return None,None
                    
                    
                
        
        


def getFilterXMLfromSQL(filters,dialect,classname):
    ET.register_namespace('wsman',"http://schemas.dmtf.org/wbem/wsman/1/wsman.xsd")
    xml=ET.fromstring('<wsman:Filter xmlns:wsman="http://schemas.dmtf.org/wbem/wsman/1/wsman.xsd"></wsman:Filter>')
    xml.attrib['Dialect']=dialect.strip()
    SQL=''
    if type(filters) is str:
        SQL=filters
    else:
        SQL="select * from %s" %classname
        if len(filters):
            putAnd=False
            for filterTuple in filters:
                left=filterTuple[0]
                right=filterTuple[1]
                queryPart=''
                if len(left):
                    querypart=left
                else:
                    continue
                if len(right):
                    querypart+=' = %s' %right
                else:
                    querypart+=' is NULL'
                
                if putAnd:
                    SQL += " and "
                else:
                    putAnd=True
                    SQL += " where "
                SQL += querypart
    xml.text=SQL

    return ET.tostring(xml)


def extractIfCompressed(xmlStr):
    isCompressed=False
    uncompressedSize=0
    compressedSize=0
    timeTaken=0.0
    if xmlStr:
        xml=ET.fromstring(xmlStr)
        tag = xml.find('CompressedData')
        compressedSize=uncompressedSize=len(xmlStr)
        if tag:
            #print "Compressed Size: %d" %compressedSize
            startTime=datetime.datetime.now()
            xmlStr=zlib.decompress(base64.b64decode(tag.text))
            endTime=datetime.datetime.now()
            timeTaken=(endTime-startTime).total_seconds()
            uncompressedSize=len(xmlStr)
            isCompressed=True
            #print "Decompressed Size: %d" %uncompressedSize
            #print "Decompression time: %f" %timeTaken
    return xmlStr, isCompressed, uncompressedSize, compressedSize, timeTaken
        
def extractSelectorsFromXML(xmlStr):
    if not xmlStr:
        return []
    ET.register_namespace('wsman',"http://schemas.dmtf.org/wbem/wsman/1/wsman.xsd")
    ET.register_namespace('wsa',"http://schemas.xmlsoap.org/ws/2004/08/addressing")
    xml=ET.fromstring(xmlStr)
    selectorSets=[]
    for child_1 in xml:
        if child_1.tag.endswith('Body'):
            for child_2 in child_1:
                if child_2.tag.endswith('EnumerateResponse') or child_2.tag.endswith('PullResponse'):
                    for child_3 in child_2:
                        if child_3.tag.endswith('Items'):
                            for child_4 in child_3:
                                if child_4.tag.endswith('EndpointReference'):
                                    for child_5 in child_4:
                                        if child_5.tag.endswith('ReferenceParameters'):
                                            selectorSets.append(ET.tostring(child_5))
                                            '''print "#####"
                                            print ET.tostring(child_5)
                                            print "#####"'''
                                            '''for child_6 in child_5:
                                                if child_6.tag.endswith('SelectorSet'):
                                                    selectorSets.append(ET.tostring(child_6))'''
                else:
                    return []
    #print selectorSets
    return selectorSets

def getSelectors(xmlStr):
    if not xmlStr:
        return []
    ET.register_namespace('wsman',"http://schemas.dmtf.org/wbem/wsman/1/wsman.xsd")
    xml=ET.fromstring(xmlStr)
    selectors=[]
    for child in xml:
        if child.tag.endswith('Selector'):
            selectors.append('%s=%s'%(child.attrib['Name'],child.text))
    return selectors

def getIdentifyXmlStr():
    data="""<?xml version="1.0"?>
<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope" xmlns:wsmid="http://schemas.dmtf.org/wbem/wsman/identity/1/wsmanidentity.xsd">
<s:Header/>
<s:Body>
<wsmid:Identify/>
</s:Body>
</s:Envelope>"""
    return data

def getExceptionXml(code,subcode,reason):
    reason=str(reason)
    if reason:
        reason=reason.replace('<','').replace('>','')
    data="""<?xml version="1.0" encoding="UTF-8"?>
<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope"><s:Body><s:Fault><s:Code><s:Value>"""+str(code)+"""</s:Value><s:Subcode><s:Value>"""+str(subcode)+"""</s:Value></s:Subcode></s:Code><s:Reason><s:Text xml:lang="en">"""+str(reason)+"""</s:Text></s:Reason></s:Fault></s:Body></s:Envelope>"""
    return data

def hasFault(xmlStr):
    bodyIndex=xmlStr.find('<s:Body>')
    if bodyIndex > 0:
        segment=xmlStr[bodyIndex:bodyIndex+20]
        if segment.find('<s:Fault>')>0:
            return True
    return False




################################################ KIRAN
def createXMLFileFromAVMap(AVMap, fileName, resourceURI, methodName):
    xmlStr="<n:%s_INPUT xmlns:n=\"%s\">\n" %(methodName,resourceURI)
    for key in AVMap.keys():
        for value in AVMap[key].split(','):
            xmlStr+="<n:%s>%s</n:%s>\n" %(key,value.strip(),key)
    xmlStr+="</n:%s_INPUT>" %methodName
    xmlFile=open(fileName,"w")
    xmlFile.write(xmlStr)
    xmlFile.close()
    
def getAVMapFromXMLFile(fileName):
    xmlFile=ET.parse(fileName)

    root=xmlFile.getroot()
    AVMap={}
    for child in root:
        name,value = child.tag.split('}')[1], child.text
        if AVMap.has_key(name):
            AVMap[name]+=', ' + value
        else:
            AVMap[name]=value
        
    return AVMap

def getFilterXml(dialect,ResourceURI,SelectorSet,typ):
    
        
    if typ == 'association':
        tagName= 'AssociationInstances'
    elif typ == 'references':
        tagName= 'AssociatedInstances'
    else:
        return None
        
    baseXmlTemplate='''<wsman:Filter xmlns:wsa="http://schemas.xmlsoap.org/ws/2004/08/addressing" xmlns:wsman="http://schemas.dmtf.org/wbem/wsman/1/wsman.xsd" xmlns:b="http://schemas.dmtf.org/wbem/wsman/1/cimbinding.xsd" Dialect="%s">
<b:%s>
<b:Object>
<wsa:Address>http://schemas.xmlsoap.org/ws/2004/08/addressing/role/anonymous</wsa:Address>
<wsa:ReferenceParameters>
<wsman:ResourceURI>%s</wsman:ResourceURI>
%s
</wsa:ReferenceParameters>
</b:Object>
</b:%s>
</wsman:Filter>'''%(dialect.strip(),tagName,ResourceURI.strip(),SelectorSet,tagName)
    #print baseXmlTemplate
    return baseXmlTemplate

def getItemsFromXmlStr(xmlStr):
    global prettyString
    def finder(xml,depth):
        global prettyString
        try:
            tagname=xml.tag.split("}")[1]
        except:
            tagname=xml.tag
        prettyString+="  "*depth + tagname
        if xml.attrib:
            for key in xml.keys():
                if key.endswith("nil"):
                    prettyString += " = " + "<Nil>"
                    break
                elif key=="Name":
                    prettyString += ": " + xml.attrib[key]
                    break
        if xml.text:
            prettyString += " = " + xml.text
        prettyString+="\n"
        for child in xml:
            finder(child,depth+1)
        
    if not xmlStr:
        return '',0,True
    xml = ET.fromstring(xmlStr)
    prettyString=''
    nItems=0
    Fault=False
    for child_1 in xml:
        if child_1.tag.endswith('Body'):
            for child_2 in child_1:
                if child_2.tag.endswith('EnumerateResponse') or child_2.tag.endswith('PullResponse'):
                    for child_3 in child_2:
                        if child_3.tag.endswith('Items'):
                            for child_4 in child_3:
                                finder(child_4,0)
                                prettyString+="\n\n"
                                nItems+=1
                else:
                    if child_2.tag.endswith('Fault'):
                        Fault=True
                    finder(child_2,0)
    return prettyString, nItems, Fault
    
        
