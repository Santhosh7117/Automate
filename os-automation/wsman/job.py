from w import wsman
#from w_bios_mgmt import wsman_BIOSMgmt
#from w_lc_mgmt import wsman_LCMgmt
#from w_nic_mgmt import *
#from w_raid_mgmt import *
from w_job_mgmt import wsman_jobMgmt
#rom w_OSDeployment_mgmt import wsman_OSDeployment
#from w_fc_mgmt import w_fc_mgmt
import logging
import sys


class job:
    def __init__(self,idrac_ip,jobid):
        
        w=wsman(idrac_ip)
        self.lc=wsman_jobMgmt(w)
        self.jobstatus(jobid)

    def jobstatus(self,jobid):
        print self.lc.getJobStatus(jobid)
        
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    p=job(sys.argv[1],sys.argv[2])

        
