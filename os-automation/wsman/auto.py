from w import wsman
from w_bios_mgmt import wsman_BIOSMgmt
import logging
from command import Command

class auto:

    def __init__(self):
        print "pra"
        self.system='M820-4HV3F02'
        self.job="bkr workflow-simple  --kernel-options='ignore_log' --family='RedHatEnterpriseLinux7' --distro='Red Hat Enterprise Linux 7.3' --arch=x86_64 --variant=Server --method=http  --task /distribution/install  --task /CoreOS/beaker/Sanity/var-log-analysis --task /distribution/beaker/Sanity/reboot-tests --taskparam=REBOOT_COUNT=10"
        self.w = wsman('100.98.4.51')
        self.bios = wsman_BIOSMgmt(self.w)
        logging.basicConfig(level=logging.DEBUG)
        
        
    def install_BIOS_PXE(self):
        name='%s --whiteboard=install_RAID_BIOS_PXE_%s'%(self.job,self.system)
         
        mode = self.bios.getbootMode()
        if mode:
            if mode != "Bios":
                self.bios.SetAttribute('bootMode', 'Bios')
                self.bios.creatAndmonitorJob()
            else:
                logging.info("Already in BIOS mode")
        else:
            logging.error("Not able to get Mode")
        cmd=Command(name)
        cmd.run()
        jid= cmd.output[0].split('[')[1].replace('\'', '').replace(']', '')
        print jid
    def install_UEFI_PXE(self):
        name='%s --whiteboard=install_RAID_UEFI_PXE_%s'%(self.job,self.system)
        mode = self.bios.getbootMode()
        if mode:
            if mode != "Uefi":
                self.bios.SetAttribute('bootMode', 'Uefi')
                self.bios.creatAndmonitorJob()
            else:
                logging.info("Already in UEFI mode")
        else:
            logging.error("Not able to get Mode")
    
pp=auto()
pp.install_BIOS_PXE()