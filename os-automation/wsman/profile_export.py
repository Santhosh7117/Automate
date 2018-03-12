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
    def __init__(self,idrac_ip,install):
        
        w=wsman(idrac_ip)
        self.bios=wsman_BIOSMgmt(w)
        self.lc=wsman_LCMgmt(w)
        self.systemName=self.getSys()
        self.profileExport('%s_%s.xml'%(self.systemName,install))
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
        #self.bios.setBIOSMode(bootMode)
        jobid=self.lc.ExportSystemConfiguration(IPAddress='100.98.4.4',ShareName='public/test',ShareType='2',FileName=name)
        self.lc.monitorJob(jobid)
        
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    if len (sys.argv) != 3 :
        print "Usage: python profile_export.py idrac_ip install:%s"%(len(sys.argv))
        sys.exit (1)
    p= profile(sys.argv[1],sys.argv[2])
        
