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
    def __init__(self,info):
        #self.iqn="iqn.2001-05.com.equallogic:0-1cb196-8568d4a2d-3f90000005a5a308-r830-automation" 
        #self.iqn="iqn.2001-05.com.equallogic:0-1cb196-e0a8d4a2d-a5a0000005d5a30e-r630-fpm1cd2"
        
        w=wsman(info['idracip'])
        self.bios=wsman_BIOSMgmt(w)
        self.lc=wsman_LCMgmt(w)
        #print w.enumerate('dcim_biosenumeration')
        self.set_iscsi()
    def set_iscsi(self):
        self.bios.SetAttribute('IscsiDev1Con1EnDis','Enabled')
        self.bios.SetAttribute('IscsiDev1con1Auth','None')
        self.bios.SetAttribute('IscsiDev1Con1DhcpEnDis','Enabled')
        self.bios.SetAttribute('IscsiDev1Con1Protocol',info['proto']) #IPv4
        self.bios.SetAttribute('IscsiDev1Con1TgtDhcpEnDis','Disabled')
        self.bios.SetAttribute('IscsiDev1Con1VlanEnDis','Disabled')
        self.bios.SetAttribute('IscsiDev1Con1TargetIp',info['tgt_ip']) #'100.98.4.16')
        self.bios.SetAttribute('IscsiDev1Con1TargetName',info['iqn'])
        self.bios.SetAttribute('IscsiDev1Con1Lun','0')
        self.bios.SetAttribute('IscsiInitiatorName',info['init']) #'iqn.2005-03.com.RedHat:r630-fpm1cd2')
        self.bios.SetAttribute('IscsiDev1EnDis','Enabled')
        self.bios.SetAttribute('IscsiDev1Con1Interface',info['nic'])  #'NIC.Integrated.1-2-1')
        self.bios.SetAttribute('IntegratedRaid','Disabled')  # integrated raid disable 
        self.bios.SetAttribute('EmbSata','Off')  # integrated raid disable 


        


        print self.bios.CreateTargetedConfigJob() 
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    info={"idracip": sys.argv[1],'nic': sys.argv[2],"init": sys.argv[3],"iqn": sys.argv[4],"tgt_ip": sys.argv[5], 'proto': sys.argv[6] }
    p= profile(info)
        
