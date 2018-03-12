from w import wsman
#from w_bios_mgmt import wsman_BIOSMgmt
#from w_lc_mgmt import wsman_LCMgmt
#from w_nic_mgmt import *
#from w_raid_mgmt import *
from w_job_mgmt import wsman_jobMgmt
from w_OSDeployment_mgmt import wsman_OSDeployment
#from w_fc_mgmt import w_fc_mgmt
import logging
import sys


class job:
    def __init__(self,idrac_ip):

        self.w=wsman(idrac_ip)
        self.os=wsman_OSDeployment(self.w)
    
        #self.attachOEMDRV(idrac_ip,sharePath,imageName)
        #self.getinfo()

    def BootToNetworkISO(self,ip,sharePath,imageName):
        print self.w.invoke('dcim_osdeploymentservice',"configurableboottonetworkiso",{" IPAddress" : "100.98.4.4","ShareName": "/test/automation","ImageName" : "f27.iso","ShareType" : "0","ResetType" : "1"})
        #print self.os.BootToNetworkISO(ip,sharePath,imageName)

    def DetachISOImage(self):
        print self.os.DetachISOImage()
    def iDRACReset(self):
        print self.w.invoke('dcim_idraccardservice', 'idracreset',{'Force':'1'})


if __name__ == '__main__':
    print len(sys.argv)
    if len(sys.argv) == 4:
        p=job(sys.argv[1])
        p.BootToNetworkISO('100.98.4.4',sys.argv[2],sys.argv[3])
    elif len(sys.argv) == 3 and sys.argv[2] == "disconnectiso":
        p=job(sys.argv[1])
        p.DetachISOImage()
    elif len(sys.argv) == 3 and  sys.argv[2] == "idracreset":
        print "reseting"
        p=job(sys.argv[1])
        p.iDRACReset()



