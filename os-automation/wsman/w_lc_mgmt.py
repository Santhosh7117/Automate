# -*- coding: utf-8 -*-
from w import wsman
from w_job_mgmt import wsman_jobMgmt
import logging
import re
import sys
class wsman_LCMgmt(wsman):
    '''
    The Lifecycle Controller (LC) Management Profile describes the management of the Dell Lifecycle
    Controller and its configuration attributes. The profile details certificate management and the LC
    configuration services that are necessary for the LC’s proper functionality. The LC configuration attributes
    are modeled as attribute collections for an individual LC; typically there is one LC per system platform.
    '''
    def __init__(self,w):
        self.conn=w
        self.job=wsman_jobMgmt(self.conn)
        
        '''SetAttribute
        SetAttributes
        CreateConfigJob()
        ReInitiateDHS()
        ReInitiateAutoDiscovery()
        ClearProvisioningServer()
        DownloadServerPublicKey()
        DownloadClientCerts()
        DeleteAutoDiscoveryClientCerts ()
        SetCertificateAndPrivateKey()
        SetPublicCertificate()
        DeleteAutoDiscoveryServerPublicKey()
        InsertCommentInLCLog()
        ExportLCLog()
        ExportCompleteLCLog()'''
    def __commonFunction(self,shareDetail,func):
        shareDetail['Username']="root"
        shareDetail['Password']="dell01"
        
        result=self.conn.invoke('dcim_lcservice', '%s'%func.lower(),shareDetail)
        print result
        if '%s_OUTPUT'%func in result.keys():
            if result['%s_OUTPUT'%func]['ReturnValue']=='4096':
                return result['%s_OUTPUT'%func]['Selector: InstanceID']
        return False
    
    def ExportLCLog(self,IPAddress,ShareName,ShareType,FileName):
        shareDetail={'IPAddress':'%s'%IPAddress,'ShareName':'%s'%ShareName,'ShareType':'%s'%ShareType,'FileName':'%s'%FileName}
        return self.__commonFunction(shareDetail,self.BackupImage.__name__)
    
    def ExportHWInventory(self,IPAddress,ShareName,ShareType,FileName):
        shareDetail={'IPAddress':'%s'%IPAddress,'ShareName':'%s'%ShareName,'ShareType':'%s'%ShareType,'FileName':'%s'%FileName}
        return self.__commonFunction(shareDetail,self.BackupImage.__name__)
    
    def ExportFactoryConfiguration(self,IPAddress,ShareName,ShareType,FileName):
        shareDetail={'IPAddress':'%s'%IPAddress,'ShareName':'%s'%ShareName,'ShareType':'%s'%ShareType,'FileName':'%s'%FileName}
        return self.__commonFunction(shareDetail,self.BackupImage.__name__)
    
    def ExportSystemConfiguration(self,IPAddress,ShareName,ShareType,FileName):
        shareDetail={'IPAddress':'%s'%IPAddress,'ShareName':'%s'%ShareName,'ShareType':'%s'%ShareType,\
                     'FileName':'%s'%FileName,'ExportUse':'2'}
        return self.__commonFunction(shareDetail,sys._getframe().f_code.co_name)
    
    def ImportSystemConfiguration(self,IPAddress,ShareName,ShareType,FileName):
        shareDetail={'IPAddress':'%s'%IPAddress,'ShareName':'%s'%ShareName,'ShareType':'%s'%ShareType,\
                     'FileName':'%s'%FileName,'ShutdownType':'0'}
        return self.__commonFunction(shareDetail,self.ImportSystemConfiguration.__name__)
    
    def BackupImage(self,IPAddress,ShareName,ShareType,ImageName):
        shareDetail={'IPAddress':'%s'%IPAddress,'ShareName':'%s'%ShareName,'ShareType':'%s'%ShareType,'ImageName':'%s'%ImageName,'ScheduledStartTime':'TIME_NOW'}
        return self.__commonFunction(shareDetail,self.BackupImage.__name__)
    
    def RestoreImage(self,IPAddress,ShareName,ShareType,ImageName):
        shareDetail={'IPAddress':'%s'%IPAddress,'ShareName':'%s'%ShareName,'ShareType':'%s'%ShareType,'ImageName':'%s'%ImageName,'ScheduledStartTime':'TIME_NOW'}
        return self.__commonFunction(shareDetail,self.RestoreImage.__name__)
    
    def TestNetworkShare(self,IPAddress,ShareName,ShareType,FileName):
        shareDetail={'IPAddress':'%s'%IPAddress,'ShareName':'%s'%ShareName,'ShareType':'%s'%ShareType,'FileName':'%s'%FileName}
        return self.__commonFunction(shareDetail,self.BackupImage.__name__)
    def CreateConfigJob(self):
        pp={'ScheduledStartTime':'TIME_NOW'}
        result=self.conn.invoke('dcim_lcservice', 'createconfigjob',pp)
        
    def monitorJob(self,jobID):
        
        if jobID:
            logging.info( "Config Job created successfully ID:%s"%(jobID))
            return self.job.monitorJob(jobID)
        else:
            print "Error: Config Job Not Created"
            return False
        '''
        LCWipe()
        TestNetworkShare()

        GetRSStatus()
        GetRemoteServicesAPIStatus ()
        ExportCertificate()
        ImportSystemConfigurationPreview()
        RunePSADiagnostics ()
        ExportePSADiagnosticsResult ()
        ExportTechSupportReport ()
        UpdateOSAppHealthData ()
        SystemErase()
        SetBackupSchedule()
        GetBackupSchedule()
        ClearBackupSchedule()
        MapMessageIdsToDetails()
        ExportErrorMsgRegistry()'''