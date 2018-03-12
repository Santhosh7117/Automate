# -*- coding: utf-8 -*-
from w import wsman
from w_job_mgmt import *
import logging


class wsman_OSDeployment:
    def __init__(self,w):
        self.conn=w

    def GetDriverPackInfo(self):
        return self.conn.invoke('dcim_osdeploymentservice', 'getdriverpackinfo',{'Version':'NULL','OSList':'NULL'})
        
    def UnpackAndAttach(self,osName,duration):
        return self.conn.invoke('dcim_osdeploymentservice', 'unpackandattach',{'OSName':'%s'%(osName),'ExposeDuration':'%s'%(duration)})
                

    def DetachDrivers(self):
        return self.conn.invoke('dcim_osdeploymentservice', 'detachdrivers',{})
        
        
    
    def UnpackAndShare(self,ip,path,os):
        arg='-k IPAddress="%s" -k ShareName="%s" -k ShareType="0" -k OSName="%s"'%(ip,path,os)
        self.wsman.invoke('UnpackAndShare', 'DCIM_OSDeploymentService', 'DCIM_ComputerSystem', arg)
        return self.wsman.parseValueFromXML('ReturnValue')[0].strip()
    
    def BootToNetworkISO(self,ip,isoPath,isoName):
        result= self.conn.invoke('dcim_osdeploymentservice', 'boottonetworkiso',{'IPAddress':'%s'%(ip),'ShareName':'%s'%(isoPath),'ShareType':'0','ImageName':'%s'%(isoName)})
        
        print result
        res=self.conn.enumerate('dcim_osdconcretejob')
        print res
        return True
    
    def DetachISOImage(self):
        result= self.conn.invoke('dcim_osdeploymentservice', 'detachisoimage',{})
        print result
        
    
    def BootToPXE(self):
        result= self.conn.invoke('dcim_osdeploymentservice', 'boottopxe',{})
        return result['BootToPXE_OUTPUT']['ReturnValue']
        
    
    def BootToHD(self):
        result= self.conn.invoke('dcim_osdeploymentservice', 'boottohd',{})
        return result['BootToHD_OUTPUT']['ReturnValue']
    
        
    
    def ConnectNetworkISOImage(self,ip,isoPath,isoName):
        result= self.conn.invoke('dcim_osdeploymentservice', 'connectnetworkisoimage',{'IPAddress':'%s'%(ip),'ShareName':'%s'%(isoPath),'ShareType':'0','ImageName':'%s'%(isoName)})
        if result['ConnectNetworkISOImage_OUTPUT']['ReturnValue'] == '4096':
            return True
        else:
            return False
    
    def getOSDConcreteJobStatus(self,instanceID):
        result=self.conn.enumerate('dcim_osdconcretejob')
        if result[instanceID]['JobStatus'] == 'Success':
            return True
        else:
            return False
    def GetNetworkISOImageConnectionInfo(self):
        result= self.conn.invoke('dcim_osdeploymentservice', 'getnetworkisoimageconnectioninfo',{})
        if result['GetNetworkISOImageConnectionInfo_OUTPUT']['ReturnValue'] == '0':
            return True
        else:
            return False
        
    
        
    def DisconnectNetworkISOImage(self):
        result= self.conn.invoke('dcim_osdeploymentservice', 'disconnectnetworkisoimage',{})
        if result['DisconnectNetworkISOImage_OUTPUT']['ReturnValue'] == '0':
            return True
        else:
            return False
        
    
    def SkipISOImageBoot(self):
        result= self.conn.invoke('dcim_osdeploymentservice', 'skipisoimageboot',{})
        if result['DisconnectNetworkISOImage_OUTPUT']['ReturnValue'] == '0':
            return True
        else:
            return False
        
        
    def ConnectRFSISOImage(self,ip,isoPath,isoName):
        result= self.conn.invoke('dcim_osdeploymentservice', 'connectnetworkisoimage',{'IPAddress':'%s'%(ip),'ShareName':'%s'%(isoPath),'ShareType':'0','ImageName':'%s'%(isoName)})
        print result
        if result['ConnectNetworkISOImage_OUTPUT']['ReturnValue'] == '4096':
            return True
        else:
            return False
        
    def GetRFSISOImageConnectionInfo(self):
        result= self.conn.invoke('dcim_osdeploymentservice', 'getrfsisoimageconnectioninfo',{})
        if result['GetNetworkISOImageConnectionInfo_OUTPUT']['ReturnValue'] == '0':
            return True
        else:
            return False
              
        
    def DisconnectRFSISOImage(self):
        print "Disconnecting RFS ISO"
        result= self.conn.invoke('dcim_osdeploymentservice', 'disconnectrfsisoimage',{})
        if result['DisconnectNetworkISOImage_OUTPUT']['ReturnValue'] == '0':
            return True
        else:
            return False
        
    
    def GetHostMACInfo(self):
        result= self.conn.invoke('dcim_osdeploymentservice', 'gethostmacinfo',{})
        print result
    
