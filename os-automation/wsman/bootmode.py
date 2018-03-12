from w import wsman
from w_bios_mgmt import wsman_BIOSMgmt
from w_lc_mgmt import wsman_LCMgmt
from w_nic_mgmt import *
from w_raid_mgmt import *
from w_OSDeployment_mgmt import wsman_OSDeployment
from w_fc_mgmt import w_fc_mgmt
import logging
import sys


class profile:
    def __init__(self,idrac_ip,mode):
        
        w=wsman(idrac_ip)
        self.bios=wsman_BIOSMgmt(w)
        self.set_bootmode(mode)
    def set_bootmode(self,mode):
        print self.bios.setBIOSMode(mode)
        
if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING)
    if len (sys.argv) != 3 :
        print "Usage: python profile_export.py idrac_ip install:%s"%(len(sys.argv))
        sys.exit (1)
    p= profile(sys.argv[1],sys.argv[2])
        
