from w import wsman
from w_bios_mgmt import wsman_BIOSMgmt
from w_lc_mgmt import wsman_LCMgmt
from w_nic_mgmt import *
from w_raid_mgmt import *
from w_OSDeployment_mgmt import wsman_OSDeployment
from w_fc_mgmt import w_fc_mgmt
import logging
import sys


class PXEBOOT:
    def __init__(self,idrac_ip):
        
        w=wsman(idrac_ip)
        self.os_deploy=wsman_OSDeployment(w)
        self.set_pxe_boot()
    def set_pxe_boot(self):
        print self.os_deploy.BootToPXE()
        
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    if len (sys.argv) != 2 :
        print "Usage: python profile_export.py idrac_ip install:%s"%(len(sys.argv))
        sys.exit (1)
    p= PXEBOOT(sys.argv[1])
        
