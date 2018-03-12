from w import wsman
from w_job_mgmt import *
import logging

import re

class wsman_RAID:
    def __init__(self,w):
        self.conn=w
    
    def getRaidType(self,vd):
        resultenum=self.conn.enumerate('dcim_virtualdiskview')
        if vd in resultenum.keys():
            return resultenum[vd]['RAIDTypes']
        else:
            return False
        
    def getEnclosure(self):
        result=self.conn.enumerate('dcim_enclosureview')
        logging.debug('Enclosure:%s'%result.keys())
        return result.keys()
        
    def getControllers(self):
        result=self.conn.enumerate('dcim_controllerview')
        logging.debug('Controller:%s'%result.keys())
        return result.keys()
    
    def getVirtualDisk(self):
        result=self.conn.enumerate('dcim_virtualdiskview')
        return result.keys()
        
    def getPhysicalDisks(self):
        result=self.conn.enumerate('dcim_physicaldiskview')
        logging.debug('PhysicalDisk:%s'%result.keys())
        return result.keys()
        
    def getSupportedRAIDLevels(self,controller):
        instanceID='%s:RAIDSupportedRAIDLevels'%(controller)
        result=self.conn.get('dcim_raidenumeration',instanceID)
        return result[instanceID]['CurrentValue']
        
        
    def getRAIDSupportedDiskProt(self,controller):
        instanceID='%s:RAIDSupportedDiskProt'%(controller)
        result=self.conn.get('dcim_raidenumeration',instanceID)
        return result[instanceID]['CurrentValue']
    
    def getRAIDSupportedInitTypes(self,controller):
        instanceID='%s:RAIDSupportedInitTypes'%(controller)
        result=self.conn.get('dcim_raidenumeration',instanceID)
        return result[instanceID]['CurrentValue']
    
        
    def getRAIDloadBalancedMode(self,controller):
        instanceID='%s:RAIDloadBalancedMode'%(controller)
        result=self.conn.get('dcim_raidenumeration',instanceID)
        print result
        return result[instanceID]['CurrentValue']
    
        
    def getRAIDccMode(self):
        name='RAIDccMode'
        controller=self.getControllers()[0]
        return self.__get('%s:%s'%(controller,name))
    def getRAIDprMode(self):
        name='RAIDprMode'
        controller=self.getControllers()[0]
        return self.__get('DCIM_RAIDEnumeration','%s:%s'%(controller,name))
    def getRAIDcopybackMode(self):
        name='RAIDcopybackMode'
        controller=self.getControllers()[0]
        return self.__get('DCIM_RAIDEnumeration','%s:%s'%(controller,name))
    def getRAIDEnhancedAutoImportForeignConfig(self):
        name='RAIDEnhancedAutoImportForeignConfig'
        controller=self.getControllers()[0]
        return self.__get('DCIM_RAIDEnumeration','%s:%s'%(controller,name))
    def getRAIDControllerBootMode(self):
        name='RAIDControllerBootMode'
        controller=self.getControllers()[0]
        return self.__get('DCIM_RAIDEnumeration','%s:%s'%(controller,name))
    def getRAIDMaxCapableSpeed(self):
        name='RAIDMaxCapableSpeed'
        controller=self.getControllers()[0]
        return self.__get('DCIM_RAIDEnumeration','%s:%s'%(controller,name))
    
    def getRAIDPDState(self,PDFQDD):
        return self.__get('DCIM_RAIDEnumeration','%s:RAIDPDState'%(PDFQDD))
    def getRAIDHotSpareStatus(self,PDFQDD):
        return self.__get('DCIM_RAIDEnumeration','%s:RAIDHotSpareStatus'%(PDFQDD))
    def getRAIDNegotiatedSpeed(self,PDFQDD):
        return self.__get('DCIM_RAIDEnumeration','%s:RAIDNegotiatedSpeed'%(PDFQDD))
    
    def getRAIDmaxSupportedVD(self):
        name='RAIDmaxSupportedVD'
        controller=self.getControllers()[0]
        return self.__get('DCIM_RAIDInteger','%s:%s'%(controller,name))[0]
        

    def RAIDmaxPDsInSpan(self):
        name='RAIDmaxPDsInSpan'
        controller=self.getControllers()[0]
        return self.__get('DCIM_RAIDInteger','%s:%s'%(controller,name))[0]
    def getRAIDmaxSpansInVD(self):
        name='RAIDmaxSpansInVD'
        controller=self.getControllers()[0]
        return self.__get('DCIM_RAIDInteger','%s:%s'%(controller,name))[0]
    def getRAIDrebuildRate(self):
        name='RAIDrebuildRate'
        controller=self.getControllers()[0]
        return self.__get('DCIM_RAIDInteger','%s:%s'%(controller,name))[0]
    def getRAIDccRate(self):
        name='RAIDccRate'
        controller=self.getControllers()[0]
        return self.__get('DCIM_RAIDInteger','%s:%s'%(controller,name))[0]
    def getRAIDreconstructRate(self):
        name='RAIDreconstructRate'
        controller=self.getControllers()[0]
        return self.__get('DCIM_RAIDInteger','%s:%s'%(controller,name))[0]
    def getRAIDbgiRate(self):
        name='RAIDbgiRate'
        controller=self.getControllers()[0]
        return self.__get('DCIM_RAIDInteger','%s:%s'%(controller,name))[0]
    def getRAIDprRate(self):
        name='RAIDprRate'
        controller=self.getControllers()[0]
        return self.__get('DCIM_RAIDInteger','%s:%s'%(controller,name))[0]
    def getRAIDspinDownIdleTime(self):
        name='RAIDspinDownIdleTime'
        controller=self.getControllers()[0]
        return self.__get('DCIM_RAIDInteger','%s:%s'%(controller,name))[0]
    def getRAIDprIterations(self):
        name='RAIDprIterations'
        controller=self.getControllers()[0]
        return self.__get('DCIM_RAIDInteger','%s:%s'%(controller,name))[0]
    def getRAIDNominalMediumRotationRate(self,PDFQDD):
        return self.__get('DCIM_RAIDInteger','%s:RAIDNominalMediumRotationRate'%(PDFQDD))
    
    
    def getPDRAIDStatus(self,PDInstanceID):
        self.wsman.get('DCIM_PhysicalDiskView','InstanceID' , '%s'%(PDInstanceID))
        values=self.wsman.parseValueFromXML('RaidStatus')
        if values :
            values = [x.strip() for x in values]
            return values[0]
        return False
    def getPDFreeSizeInBytes(self,PDInstanceID):
        self.wsman.get('DCIM_PhysicalDiskView','InstanceID' , '%s'%(PDInstanceID))
        values=self.wsman.parseValueFromXML('FreeSizeInBytes')
        if values :
            values = [x.strip() for x in values]
            return values[0]
        return False
    

    
    def assignSpareDisk(self,fqdd,vdNameList):
        arg = '-k Target="%s" -k "VirtualDiskArray=%s" ' % (fqdd)
        self.wsman.invoke('AssignSpare', 'DCIM_RAIDService', 'DCIM_ComputerSystem', arg)
        return self.wsman.parseValueFromXML('ReturnValue')[0].strip()

        
    def resetConfig(self,ControllerFQDD):
        result=self.conn.invoke('dcim_raidservice','resetconfig',{'Target':'%s'%ControllerFQDD})
        return result['ResetConfig_OUTPUT']['ReturnValue']
        
    
    def clearForeignConfig(self,ControllerFQDD):
        arg = '-k Target="%s"' % (ControllerFQDD)
        self.wsman.invoke('ClearForeignConfig', 'DCIM_RAIDService', 'DCIM_ComputerSystem', arg)
        return self.wsman.parseValueFromXML('ReturnValue')[0].strip()

    def deleteVirtualDisk(self,vdFQDD):
        print "Deleting Virtual Disk %s"%(vdFQDD)
        
        
        result=self.conn.invoke('dcim_raidservice','deletevirtualdisk',{'Target':'%s'%vdFQDD})
        print result
        print result['DeleteVirtualDisk_OUTPUT']['ReturnValue']
        #print result['DeleteVirtualDisk_OUTPUT']['Selector: InstanceID']
        if result['DeleteVirtualDisk_OUTPUT']['ReturnValue'] == '4096':
            return result['DeleteVirtualDisk_OUTPUT']['Selector: InstanceID']
        else:
            return False
        
    def createVirtualDisk(self,PDFQDD,level,depth,length,name="VD"):
        print "Creating Virtual Disk With:"
        if level =='2':
            print 'RAID0'
        elif level == '4':
            print 'RAID1'
        elif level =='64':
            print 'RAID5'
        elif level == '128':
            print 'RAID6'
        print "Physical disks:"
        for i in PDFQDD:
            print i
        print 'Name:%s'%name
        
        ller=self.getControllers()
        ctr=filter(lambda x: 'RAID' in x,ller)
        if len(ctr) > 0:
            controller = ctr[0]
        else:
            logging.error('Controller not found')
            return False
        pd=None
        for i in PDFQDD:
            if pd != None:
                pd=pd+','+i
            else:
                pd=i
        param={'Target':'%s'%controller,
               'PDArray':'%s'%(pd),
               'VDPropNameArray':'Initialize,RAIDLevel,VirtualDiskName,SpanDepth,SpanLength',
               'VDPropValueArray':'0,%s,%s,%s,%s'%(level,name,depth,length) }
        
        result=self.conn.invoke('dcim_raidservice','createvirtualdisk',param)
        print result
        print result['CreateTargetedConfigJob_OUTPUT']['ReturnValue']
        print result['CreateTargetedConfigJob_OUTPUT']['Selector: InstanceID']
        if result['CreateTargetedConfigJob_OUTPUT']['ReturnValue'] == '4096':
            return result['CreateTargetedConfigJob_OUTPUT']['Selector: InstanceID']
        else:
            return False
        
    def InitializeVirtualDisk(self,vdFQDD):
        print "Start initialize Virtual Disk %s"%vdFQDD
        arg = '-k "VirtualDisk=%s"  -k "InitType=1"' % (vdFQDD)
        self.wsman.invoke('DeleteVirtualDisk', 'DCIM_RAIDService', 'DCIM_ComputerSystem', arg)
        return self.wsman.parseValueFromXML('ReturnValue')[0].strip()
    
    
    def GetDHSDisks(self,vdFQDD):
        
        result=self.wsman.invoke('dcim_raidservice','getdhdisks',{'Target':'%s'%(vdFQDD)})
        print result
        #pd=self.wsman.parseValueFromXML('PDArray')
        #pd=[x.strip() for x in pd]
        #return pd

    
    def GetRAIDLevels(self,ControllerFQDD,DiskType=0,Diskprotocol=0):
        arg='-k "Target=%s" -k "DiskType=%s" -k "Diskprotocol=%s"'%(ControllerFQDD,DiskType,Diskprotocol)
        self.wsman.invoke('GetRAIDLevels','DCIM_RAIDService' , 'DCIM_ComputerSystem', arg)
        
    def GetAvailableDisks(self,controller,DiskType=0,Diskprotocol=0):
        
        self.conn.invoke('dcim_raidservice','getavailabledisks',{'Target':'%s'%(controller),'DiskType':'%s'%DiskType, 'Diskprotocol':'%s'%Diskprotocol})
        
        return 
    
    def CheckVDValues(self,param):
        self.wsman.writexml('/tmp/RAID_attr.xml',param, 'DCIM_RAIDService')
        arg = '-J "%s" '%('/tmp/RAID_attr.xml')
        self.wsman.invoke('CreateVirtualDisk', 'DCIM_RAIDService', 'DCIM_ComputerSystem', arg)
        return self.wsman.parseValueFromXML('ReturnValue')[0].strip() 
    
    def SetControllerKey(self,ControllerFQDD,key,keyid):
        arg = '-k "Target=%s" -k "Key=%s" -k "keyid=%s"'%(ControllerFQDD,key,keyid)
        self.wsman.invoke('SetControllerKey', 'DCIM_RAIDService', 'DCIM_ComputerSystem', arg)
        return self.wsman.parseValueFromXML('ReturnValue')[0].strip() 
    
    def LockVirtualDisk(self):
        pass
    def CreateTargetedConfigJob(self,fqdd,RebootJobType='1',ScheduledStartTime=None):
        if ScheduledStartTime:
            result=self.conn.invoke('dcim_raidservice' ,'createtargetedconfigjob', {'Target':'%s'%(fqdd),'RebootJobType':'1'})
            
        else:
            result=self.conn.invoke('dcim_raidservice','createtargetedconfigjob', {'Target':'%s'%(fqdd),'RebootJobType':'1','ScheduledStartTime':'%s'%(ScheduledStartTime)})
            
        if result['CreateTargetedConfigJob_OUTPUT']['ReturnValue'] == '4096':
            return result['CreateTargetedConfigJob_OUTPUT']['Selector: InstanceID']
        else:
            return False
       
    
    def DeletePendingConfiguration(self):
        pass
    def SetAttribute(self):
        pass
    def SetAttributes(self):
        pass
    
    def RemoveControllerKey(self):
        pass
    def EnableControllerEncryption(self):
        pass
    def ReKey(self):
        pass

    def unassignSpare(self,pdisk):
        #error msg = Physical disk FQDD did not identify a valid physical disk for the operation
        arg='-k "Target=%s"'%(pdisk)
        self.wsman.invoke('UnassignSpare', 'DCIM_RAIDService', 'DCIM_ComputerSystem', arg)
        return self.wsman.parseValueFromXML('ReturnValue')[0].strip()    
    
    def convertToRAID(self,*pdisk):
        arg='-k "Target=%s"'%(pdisk)
        self.wsman.invoke('ConvertToRAID', 'DCIM_RAIDService', 'DCIM_ComputerSystem', arg)
        return self.wsman.parseValueFromXML('ReturnValue')[0].strip()
     
    def convertToNonRAID(self,*pdisk):
        arg='-k "Target=%s"'%(pdisk)
        self.wsman.invoke('ConvertToNonRAID', 'DCIM_RAIDService', 'DCIM_ComputerSystem', arg)
        return self.wsman.parseValueFromXML('ReturnValue')[0].strip()
    
   
   
    def monitorJob(self):
        jobID=self.wsman.parseValueFromXML('JID_')[0].strip()
        print "job id :" + jobID
        j=wsman_jobMgmt(self.options['hostName'].split(' ')[1])
        return j.monitorJob(jobID)
    
    def deleteAllVD(self):
        vds=self.getVirtualDisk()
        if vds:
            for vd in vds:
                print self.deleteVirtualDisk(vd)
                
    def __get(self,className,typeValue):
        self.wsman.get(className,'InstanceID' , '%s'%(typeValue))
        values=self.wsman.parseValueFromXML('CurrentValue')
        if values :
            values = [x.strip() for x in values]
            return values
        return False
    
    def createRAID0(self,PDFQDD,level,depth,length):
        controller=self.getControllers()[0]
        #pd=self.getPhysicalDisks()
        pd=None
        for i in PDFQDD:
            if pd != None:
                pd=pd+','+i
            else:
                pd=i
        param={'Target':'%s'%controller,
               'PDArray':'%s'%(pd),
               'VDPropNameArray':'RAIDLevel,VirtualDiskName,SpanDepth,SpanLength',
               'VDPropValueArray':'2,vDiskNameHere,1,2' }
        self.createVirtualDisk(param)

    def creatAndmonitorJob(self,fqdd,delay='TIME_NOW'):
        jobID =self.CreateTargetedConfigJob(fqdd,delay)
        if jobID:
            logging.info( "Config Job created successfully ID:%s"%(jobID))
            return self.job.monitorJob(jobID)
        else:
            print "Error: Config Job Not Created"
            return False



