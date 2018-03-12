from w import wsman
from w_bios_mgmt import wsman_BIOSMgmt
from w_lc_mgmt import wsman_LCMgmt
from w_nic_mgmt import *
from w_raid_mgmt import *
from w_OSDeployment_mgmt import wsman_OSDeployment
from w_fc_mgmt import w_fc_mgmt
import logging


class profile:
    def __init__(self):
        self.profiles=['Bios_RAID0_PXEv4','Uefi_RAID0_PXEv4','Bios_RAID1_PXEv4','Uefi_RAID1_PXEv4']

        w=wsman('100.98.6.129')
        self.bios=wsman_BIOSMgmt(w)
        self.lc=wsman_LCMgmt(w)
        self.systemName=self.getSys()
        for p in self.profiles:
            self.profileExport('%s_%s'%(self.systemName,p))
    def getSys(self):
        result = self.bios.conn.enumerate('dcim_systemview')
        if result:
            m = result['System.Embedded.1']['Model']
            model = m.replace('PowerEdge', '').strip()
            tag = result['System.Embedded.1']['ServiceTag']
            return "%s-%s" % (model, tag)
        else:
            logging.error("enumation failed result:")
            logging.debug(result)
            return False
    def profileExport(self,name):
        bootMode=name.split('_')[1]
        self.bios.setBIOSMode(bootMode)
        jobid=self.lc.ExportSystemConfiguration(IPAddress='100.98.4.4',ShareName='public/test/automation/profiles/R320-GSG2G2S',ShareType='2',FileName=name)
        self.lc.monitorJob(jobid)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    p= profile()
    
