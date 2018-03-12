# -*- coding: utf-8 -*-
from w import wsman
from w_job_mgmt import wsman_jobMgmt
import logging
import re
class wsman_BIOSMgmt(wsman):
    '''
    
    '''
    def __init__(self,w):
        self.conn=w
        self.job=wsman_jobMgmt(self.conn)
    def getBootSourcesInstanceID(self):
        '''
        
        '''
        logging.debug('getBootSourcesInstanceID')
        return self.conn.enumerate('dcim_bootsourcesetting')
    
    def getbootMode(self):
        '''
        
        '''
        logging.debug('inside getbootMode')
        p=self.conn.get('dcim_biosenumeration', 'BIOS.Setup.1-1:BootMode')
        return p['BIOS.Setup.1-1:BootMode']['CurrentValue']
    
    def getIntegratedRaidControllerStatus(self):
        '''
        
        '''
        logging.debug("getting RAID controller status")
        p=self.conn.get('dcim_biosenumeration','BIOS.Setup.1-1:IntegratedRaid')
        return p['BIOS.Setup.1-1:IntegratedRaid']['CurrentValue']
    
    def getBootSequence(self,instanceID):
        '''
        
        :param instanceID:
        '''
        logging.debug('inside getBootSequence')
        p=self.conn.get('dcim_bootsourcesetting', instanceID)
        return p[instanceID]['CurrentAssignedSequence']
    
    def getSlotStatus(self, slot):
        '''
        
        :param slot:
        '''
        logging.debug("gettting current status of slot %s"%(slot))
        #result=self.conn.enumerate('dcim_biosenumeration')
        #print result
        result=self.conn.get('dcim_biosenumeration',  'bios.setup.1-1:%s'%slot)
        if 'BIOS.Setup.1-1:' in result:
            return result['BIOS.Setup.1-1:%s'%slot]['CurrentValue']
        else:
            return result
    
    def getIntegratedNetwork1Status(self):
        result=self.conn.get('dcim_biosenumeration',  'bios.setup.1-1:IntegratedNetwork1')
        if result:
            return result['BIOS.Setup.1-1:IntegratedNetwork1']['CurrentValue']
        else:
            logging.error("getIntegratedNetwork1Status Failed")
            return False
    
    def getIntegratedNetwork2Status(self):
        result=self.conn.get('dcim_biosenumeration',  'bios.setup.1-1:IntegratedNetwork2')
        return result['BIOS.Setup.1-1:IntegratedNetwork2']['CurrentValue']
    
    def getBootSourceInstanceID(self,mode):
        IDs=[]
        logging.debug("gettting all bootable IDs %s")
        result=self.conn.enumerate('dcim_bootsourcesetting')
        for i in result.keys():
            if result[i]['CurrentEnabledStatus'] ==  '1':
                if mode == 'Uefi' and re.match('^UEFI:',result[i]['InstanceID'],re.I|re.M):
                    #print result[i]['InstanceID']
                    IDs.append(result[i]['InstanceID'])
                elif mode == 'Bios' and re.match('^IPL',result[i]['InstanceID'],re.I|re.M) or re.match('^BVC',result[i]['InstanceID'],re.I|re.M):
                    IDs.append(result[i]['InstanceID'])
            
        return IDs
    def getPendingAssignedSequence(self):
        IDs=[]
        logging.debug("gettting all bootable IDs %s")
        result=self.conn.enumerate('dcim_bootsourcesetting')
        for i in result.keys():
            if result[i]['PendingAssignedSequence'] != result[i]['CurrentAssignedSequence']:
                return True
            else:
                continue
        return False
                    
    def getBootSourcePendingEnabledStatus(self):
        result=self.conn.enumerate('dcim_bootsourcesetting')
        for i in result.keys():
            if result[i]['PendingEnabledStatus']=='1':
                #print 
                return True
        return False
    def SetAttribute(self, name, value):
        '''
        
        :param name:
        :param value:
        '''
        result=self.conn.invoke('dcim_biosservice', 'setattribute',{'Target':'BIOS.Setup.1-1','AttributeName':'%s'%name, 'AttributeValue':'%s'%value})
        if 'SetAttribute_OUTPUT' in result.keys():
            if result['SetAttribute_OUTPUT']['ReturnValue']=='0':
                return True
        return False
    
    def enableSlot(self,slot,status='Enabled'):
        '''
        
        :param slot:
        :param status:
        '''
        logging.debug( "setting  %s to %s"%(slot,status))
        val = self.getSlotStatus(slot)
        if val != status:
            return self.SetAttribute(slot, status)
        else:
            return True
    
    
    def enableRaidController(self,status='Enabled'):
        '''
        
        :param status:
        '''
        logging.debug( "setting  RAID Controller to %s"%(status))
        return self.SetAttribute('IntegratedRaid', '%s'%status)
    
    def SetAttributes(self,names, values):
        '''
        
        :param names:
        :param values:
        '''
        result=self.conn.invoke('dcim_biosservice', 'setattributes',{'Target':'BIOS.Setup.1-1','AttributeName':names, 'AttributeValue':values})
        if result['SetAttributes_OUTPUT']['ReturnValue']=='0':
            return True
        else:
            return False
    def enableSlots(self,slots,status='Enabled'):
        '''
        
        :param slots:
        :param status:
        '''
        logging.debug("Disabling %s controller"%(slots))
        st=None
        for i in range(0,len(slots.split(','))):
            if st:
                st+=',%s'%status
            else:
                st=status
        result=self.SetAttributes(slots, st)
        return result
    
    def CreateTargetedConfigJob(self,delay=None):
        '''
        
        '''
        if delay:
            result=self.conn.invoke('dcim_biosservice', 'createtargetedconfigjob',{'Target':'BIOS.Setup.1-1','RebootJobType':'1','ScheduledStartTime':'%s'%(delay)})
        else:
            result=self.conn.invoke('dcim_biosservice', 'createtargetedconfigjob',{'Target':'BIOS.Setup.1-1','ScheduledStartTime':'TIME_NOW'})
        if 'CreateTargetedConfigJob_OUTPUT' in result:
            if result['CreateTargetedConfigJob_OUTPUT']['ReturnValue'] == '4096':
                return result['CreateTargetedConfigJob_OUTPUT']['Selector: InstanceID']
        else:
            return False
        
    def DeletePendingConfiguration(self):
        '''
        
        '''
        result=self.conn.invoke('dcim_biosservice', 'deletependingconfiguration',{'Target':'BIOS.Setup.1-1'})
        #print result
        if result:
            return True
        else:
            return False
        
    
    def ChangeBootSourceState(self,state,source):
        '''
        
        :param instanceID:
        :param state:
        '''
        result=self.conn.invoke('dcim_biosservice', 'changebootsourcestate',{'Target':'BIOS.Setup.1-1','EnabledState':'%s'%state,'source':'%s'%source})
        #print result
        if result:
            return True
        else:
            return False
        
    def ChangeBootOrderByInstanceID(self,typeInstance,source):
        
        result=self.conn.invoke('dcim_bootconfigsetting', 'changebootorderbyinstanceid',{'source':'%s'%source})
        #print result
        if result:
            return True
        else:
            return False
    
    def creatAndmonitorJob(self,delay='TIME_NOW'):
        jobID =self.CreateTargetedConfigJob(delay)
        if jobID:
            logging.info( "Config Job created successfully ID:%s"%(jobID))
            #return self.job.monitorJob(jobID)
            return jobID
        else:
            #print "Error: Config Job Not Created"
            return False


    def oneTimeBoot(self,instanceID):
        return self.ChangeBootOrderByInstanceID('OneTime',instanceID)
    

    def setToFirstboot(self,instanceID,pos,job=True):
        #print "Setting %s to boot position:%s"%(instanceID,pos)
        self.nextBoot(instanceID)
        return True
    
        #print "Setting %s to boot position:%s"%(instanceID,pos)
        #self.DeletePendingConfiguration('BIOS.Setup.1-1')
        cCount=self.getBootSequence(instanceID)
        if cCount:
            if pos == cCount:
                #print "%s already in sequence %s"%(instanceID,pos)
                return True
        else:
            #print "not able to get boot sequence"
            return False
        count=0
        result=self.conn.get('dcim_bootsourcesetting', instanceID)
        #print result
        
        if result[instanceID]['CurrentAssignedSequence'] == pos:
        #if self.wsman.parseValueFromXML('CurrentAssignedSequence')[0].strip()==pos:
            #print '%s already at %s position'%(instanceID,pos)
            return True
        while result[instanceID]['PendingAssignedSequence'] !=pos and count < 10:
        #while  self.wsman.parseValueFromXML('PendingAssignedSequence')[0].strip() != pos and count < 10:
            self.ChangeBootOrderByInstanceID('IPL',instanceID )
            count=count+1
            self.conn.get('dcim_bootsourcesetting',instanceID)
        
        if self.getBootSourcePendingEnabledStatus():
                self.creatAndmonitorJob()
                
        else:
            print "Already %s at position:%s"%(instanceID,pos)
    
    
    def getOneTimeBootModeEnabled(self):
        instanceID='BIOS.Setup.1-1:OneTimeBootMode'
        r= self.conn.get('dcim_biosenumeration',)
        return r[instanceID]['CurrentValue']
        
    def setOneTimeBoot(self,bootSource):

        names='OneTimeBootMode,OneTimeBootSeqDev'
        values='OneTimeBootSeq,%s'%(bootSource)
        self.SetAttributes(names, values)
        self.creatAndmonitorJob()
        
    def getBootStateEnabled(self,instanceID):
        result =self.conn.enumerate('dcim_bootsourcesetting')
        return result[instanceID]['CurrentEnabledStatus']
    
    def setBIOSMode(self,mode):
        if self.getbootMode() != mode:
            logging.debug( "setting %s mode"%(mode))
            ret = self.SetAttribute('BootMode', mode)
            if ret !=False:
                logging.debug( "changing BOOTMODE to %s"%(mode))
                #print self.job.DeleteJobQueue()
                return self.creatAndmonitorJob('TIME_NOW')
            else:
                logging.error("not able to set BOOTMODE to %s"%(mode))
                return False
        else:
            logging.info( "Already in %s Mode"%(mode))
            return True
        

