import xml.etree.ElementTree as ET

class testconfig:
    def __init__(self,configFile):
        '''
        Pass the config.xml file path, while creating object
        '''
        self.configFile=configFile
        #"/root/v8/v7/config_updated.xml"
        self.tree = ET.parse(self.configFile)
        self.root = self.tree.getroot()
        
        self.__parse()
    def __parse(self):
        self.tree = ET.parse(self.configFile)
        self.root = self.tree.getroot()
        #print self.root[0].tag
        #for child in self.root:
        #    print child.tag, child.attrib
        
        
    def getSupportedOS(self,testName):
        '''
        Method to get supported OS from config.xml file
        parameter : test case name
        '''
        for child in self.root:
            if child.attrib['name'] == testName:
                return child.get('os_version').split(',')
        
    def getDiscription(self,testName):
        '''
        Method to get Description of test from config.xml file
        parameter : test case name
        '''
        for child in self.root:
            if child.attrib['name'] == testName:
                return (child.find('description').text).lstrip().replace('\n',' ')
    def getTestCases(self):
        test=[]
        for child in self.root:
            test.append(child.attrib['name'])
        test.remove('general')
        return test

    def getTestCases1(self,system):
        l=[]
        for child in self.root:
            for gchild in child:
                for ggchild in gchild:
                    if ggchild.attrib['name'] != 'general':
                        l.append(ggchild.attrib['name'])
                         
                        
                        
        
        return l
    
    def getTestCases2(self,system,test):
        l={}
        param=""
        for child in self.root:
            for gchild in child:
                for ggchild in gchild:
                    if ggchild.attrib['name'] != 'general':
                        for gggchild in ggchild.findall('testcase'):
                            param=""
                            for i in gggchild:
                                val=i.tag+':'+i.text
                                if param == "":
                                    param=val
                                else:
                                    param=param+','+val
                            l[gggchild.attrib['name']]=param
        return l
        
    def getParameters(self,test):
        '''
        Method to get parameter name and value of specific test from config.xml file
        parameter : test case name
        Return : returns a dictionary (key-value pair) of parameter name and parameter value
        '''
        param={}
        for child in self.root:
            if child.attrib['name'] == test:
                for p in child.find('parameters'):
                    if p.tag in param:
                        param[p.tag]=param[p.tag]+','+p.text
                    else:
                        param[p.tag]=p.text
        return param
    def getParameters1(self,system,test):
        '''
        Method to get parameter name and value of specific test from config.xml file
        parameter : test case name
        Return : returns a dictionary (key-value pair) of parameter name and parameter value
        '''
        param={}
        for child in self.root:
            if child.attrib['name'] == system:
                for gchild in child:
                    for ggchild in gchild:
                        if ggchild.attrib['name'] == test:
                    
                            for p in ggchild.find('parameters'):
                                if p.tag in param:
                                    param[p.tag]=param[p.tag]+','+(p.text).replace('\n','').replace('\t','')
                                else:
                                    param[p.tag]=(p.text).replace('\n','').replace('\t','')
                
        return param
    def getSystems(self):
        l=[]
        for child in self.root:
            l.append( child.attrib['name'])
        return l
    def addParameter(self,testName,param,value):
        '''
        Method to add new parameter of specific test to config.xml file
        parameter : test case name, paramter name, value of parameter
        '''
        flag = False
        for child in self.root:
            #print child.attrib['name']
            if child.attrib['name'] == testName:
                for p in child.find('parameters'):
                        a = ET.SubElement(child.find('parameters'), param)
                        a.text = value
                        flag = True
                        break   
                else:
                    for p in child:
                        if p.tag == 'parameters':
                            #print "sssssss"
                            child.remove(p)
                            flag = True
                            a = ET.SubElement(child,'parameters')
                            b = ET.SubElement(a,param)
                            b.text = value
                            break                
        if flag:    
            self.tree.write(self.configFile)
            return True
        else:
            return False
               
        
    def removeParameter(self,testName,param):
        '''
        Method to remove parameter of specific test from config.xml file
        parameter : test case name, parameter name to be removed
        '''
        flag = False
        for child in self.root:
            if child.attrib['name'] == testName:
                for p in child:
                    for i in p:
                        if i.tag == param:
                            p.remove(i)
                            flag = True
                            break
        if flag:                
            self.tree.write(self.configFile)
            return True
        else:
            return False
    def getConfigs(self):
        tmp=dict()
        for child in self.root:
            for gchild in child:
                tmp[gchild.tag]=gchild.text
        return tmp
    def updateParameter(self,testName,param,value):
        '''
        Method to update value of already existing parameter of specific test
        parameter : test case name, paramter name, value of parameter
        '''
        flag = False
        for child in self.root:
            if child.attrib['name'] == testName:
                for p in child.find('parameters'):
                    if p.tag == param:
                        p.text = value
                        flag = True
                        break
        if flag:
            self.tree.write(self.configFile)
            #self.tree.write('/root/v8/v7/config_updated.xml')
            return True
        else:
            return False

#if __name__ == '__main__':
#    configFile="/home/git/v8-server/tests.xml"
#    conf=testconfig(configFile)
    #print conf.getSystems()
    #print conf.getParameters1('m820-4hv3f02','install_RAID6_Uefi_PXE')
#    print conf.getTestCases1('m820-4hv3f02')
#    print "hello"
#    print                         
    #p =testconfig("/home/git/v8-server/tests.xml")
#    name='install_RAID0_BIOS_PXE'
#    n= name.split('_')
#    if n[0]=='install':
#        if 'RAID' in n[1]:
 
    #print p.getParameters('install_RAID0_BIOS_PXE')
    #print p.getParameters("IpmitoolUtils")
    #print p.addParameter('cpu_info','xyz','5')
    #print p.setParameter('networking_NM_bonding_803_3ad','interfaces','em3')
    #print p.getSupportedOS('cpu_info')
    #print p.getDiscription('cpu_info') 
    #print p.getParameters('cpu_info')
    #print p.getParameterValus('networking_NM_bonding_803_3ad')
    #print p.setParameter('cpu_info','processors','5')
    #print p.addParameter('networking_NM_bonding_balance_rr','new234','hello')
    #print p.addParameter('networking_NM_bonding_balance_rr','abc','5')
    #print p.addParameter('abc','abc','5')
    #print p.addParameter('cpu_info','abc','5')
    #print p.removeParameter('cpu_info','cpu_cores')
    #print p.addParameter('networking_NM_bonding_balance_alb','new12','2000')
