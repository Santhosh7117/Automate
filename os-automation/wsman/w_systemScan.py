from w import wsman
#from w_job_mgmt import *
from w_bios_mgmt import wsman_BIOSMgmt
from w_nic_mgmt import wsman_NICMgmt
from w_raid_mgmt import wsman_RAID
# from w_OSDeployment_mgmt import *
# from w_job_mgmt import wsman_jobMgmt
import logging
import sys


class systemScan:
    def __init__(self):
        
        listSystem=['100.98.4.76']
        listIscsiTargetIQN=['iqn.2001-05.com.equallogic:0-8a0906-47ca2ae0a-1df0998807e57c3c-automation2']
        listIscsiInit=['iqn.2000-04.com.iscsi:automation2']
        listIscsiStaticIPv4=['100.98.4.6']
        listIscsiStaticIPv6=['fc00::6']
        
        self.fd=open('sys.xml','w')
        
        self.fd.write('<systems>\n')
        
        for system in listSystem:
            self.w_init(system)
            self.fd.write('<system name="%s">\n'%(self.systemName))
            self.fd.write('<tests>\n')
            self.genTest()
            self.RAIDTests()
            self.ISCSITests()
            self.fd.write('</tests>\n')
            self.fd.write('</system>\n')
        self.fd.write('</systems>\n')
        
    def w_init(self,ip):
        self.server_ip = ip
        self.OSFamily = 'RedHatEnterpriseLinux7'
        self.OSDistro = 'Red Hat Enterprise Linux 7.3'
        self.rebootCount = 10
        self.idrac = ''
        self.ports =[]
        self.conn = wsman(self.server_ip)
        self.bios = wsman_BIOSMgmt(self.conn)
        self.nic = wsman_NICMgmt(self.conn)
        self.raid = wsman_RAID(self.conn)
        self.ports = self.nic.getAllNIC()
        self.remove()
        self.pxeNIC = self.pxeSupport()
        self.iscsiNIC=[]
        self.fcoeNIC=[]
        self.iscsiNIC = self.iscsiSupport()
        self.fcoeNIC = self.fcoeSupport()
        self.nn = []
        self.systemName = self.getSys()
        self.biosdevname = ','.join(self.nic.biosdevName())
        #self.fd = open('sys.xml', 'w')
        self.iscsi = 'broadcom'
        self.RAIDController = self.getRaidC()

    def iscsiSupport(self):
        iscsiList = []
        for i in self.ports:
            result = self.nic.getiSCSIBootSupport(i)
            if result:
                iscsiList.append(i)
        for i in range(0, len(iscsiList)):
            print '%s:%s' % (i, iscsiList[i])
        iscsiPort = input('Please Select NIC for ISCSI: ')
        logging.debug('ISCSI Port:%s' % (iscsiList[iscsiPort]))
        return iscsiList[iscsiPort]

    def fcoeSupport(self):
        fcoeList = []
        for i in self.ports:
            result = self.nic.getFCoEBootSupport(i)
            if result:
                fcoeList.append(i)
        for i in range(0, len(fcoeList)):
            print '%s:%s' % (i, fcoeList[i])
        fcoePort = input('Please Select NIC for FCoE: ')

        logging.debug('fcoe Port:%s' % (fcoeList[fcoePort]))
        return fcoeList[fcoePort]

    def pxeSupport(self):
        pxeList = []
        for i in self.ports:
            result = self.nic.getPXEBootSupport(i)
            if result:
                pxeList.append(i)
        for i in range(0, len(pxeList)):
            print '%s:%s' % (i, pxeList[i])
        pxePort = input('Please Select NIC for PXE: ')

        logging.debug('PXE Port:%s' % (pxeList[pxePort]))
        return pxeList[pxePort]

    def otherNIC(self):
        for i in self.ports:
            if i in self.iscsiNIC or i in self.pxeNIC or i in self.fcoeNIC:
                continue
            else:
                self.nn.append(i)
    
        
    def remove(self):
        if  self.ports == []:
            return False
        for i in self.ports:
            if 'Slot' in i:
                s = i.split('.')[2]
                slot = 'Slot%s' % (s.split('-')[0])
                print slot
                if self.bios.getSlotStatus(slot) == 'Disabled':
                    self.ports = [x for x in self.ports if not x.startswith('NIC.Slot.%s' % s.split('-')[0])]
                    # self.ports.remove(i)
            if 'Integrated' in i:
                if 'Disabled' in self.bios.getIntegratedNetwork1Status():
                    self.ports = [x for x in self.ports if not x.startswith('NIC.Integrated')]

    def RAIDDisk(self, pd, level, raidLevel, mode, bSource):
        self.fd.write('<test name = "install_%s_%s_%s">\n' % (raidLevel, mode, bSource))
        self.fd.write('<parameters>\n')
        self.fd.write('<level>%s</level>\n' % level)
        self.fd.write('<spandepth>1</spandepth>\n')
        self.fd.write('<spanlength>%s</spanlength>\n' % (len(pd)))
        for i in pd:
            self.fd.write('<disk>%s</disk>\n' % (i))
        self.getPXENIC()
        self.otherNIC()
        self.getRAIDController()
        self.fd.write('</parameters>\n')
        self.wTestCases('/CoreOS/beaker/Sanity/var-log-analysis', ['LOG_FILE'], ['/var/log/messages'])
        #self.wTestCases('/installation/beaker/Install/check-installation', ['INSTALL_MODE_CHECK_VALUE'], ['%s' % raidLevel])
        #self.wTestCases('/kernel/beaker/Stress/CPU-stress', ['CPU_BURN_TIME'], ['10'])
        
        #self.wTestCases('/kernel/beaker/Sanity/biosdevname-sanity', ['BIOSDEVNAME'], ['%s' % self.biosdevname])
        #self.wTestCases('/kernel/prabhakar/Sanity/storage-sanity', [], [])
        #self.wTestCases('/kernel/beaker/Stress/bandwidth-testing', [], [])
        #self.wTestCases('/kernel/beaker/Sanity/ethtool-self-test', ['NIC_INTERFACE_NAME'], ["%s" % (self.biosdevname)])
        #if mode == "Uefi":
        #    self.wTestCases('/kernel/prabhakar/Sanity/UEFI-secure-boot', [], [])
        self.wTestCases('/distribution/beaker/Sanity/reboot-tests', ['REBOOT_COUNT'], ['%s' % (self.rebootCount)])
        self.fd.write('</test>\n')

    def getRaidC(self):
        c = self.raid.getControllers()
        if len(c) > 0:
            for ct in c:
                if 'AHCI' in ct:
                    continue
                else:
                    return ct
        return None

    def getRAIDController(self):
        self.fd.write('<PERC>%s</PERC>\n' % (self.RAIDController))

    def getPXENIC(self):
            self.fd.write('<PXE>%s</PXE>\n' % (self.pxeNIC))

    def getIscsiNIC(self, value='None'):
        self.fd.write('<ISCSI>%s</ISCSI>\n' % (self.iscsiNIC))

    def getFcoeNIC(self, value='None'):
        self.fd.write('<FCoE>%s</FCoE>\n' % (self.fcoeNIC))

    def RAIDTests(self):
        pd = self.raid.getPhysicalDisks()
        # print pd
        if len(pd) >= 1:
            self.RAIDDisk(pd, '2', 'RAID0', 'Bios', 'PXE')
            self.RAIDDisk(pd, '2', 'RAID0', 'Uefi', 'PXE')
            '''self.RAIDDisk(pd,'2','RAID0','Bios','RFS')
            self.RAIDDisk(pd,'2','RAID0','Uefi','RFS')'''
        if len(pd) >= 2:
            self.RAIDDisk(pd, '4', 'RAID1', 'Bios', 'PXE')
            self.RAIDDisk(pd, '4', 'RAID1', 'Uefi', 'PXE')
            '''self.RAIDDisk(pd,'4','RAID1','Bios','RFS')
            self.RAIDDisk(pd,'4','RAID1','Uefi','RFS')'''
            
        if len(pd) >= 4:
            self.RAIDDisk(pd, '64', 'RAID5', 'Bios', 'PXE')
            self.RAIDDisk(pd, '128', 'RAID6', 'Bios', 'PXE')
            self.RAIDDisk(pd, '64', 'RAID5', 'Uefi', 'PXE')
            self.RAIDDisk(pd, '128', 'RAID6', 'Uefi', 'PXE')
            
            '''self.RAIDDisk(pd,'64','RAID5','Bios','RFS')
            self.RAIDDisk(pd,'128','RAID6','Bios','RFS')
            self.RAIDDisk(pd,'64','RAID5','Uefi','RFS')
            self.RAIDDisk(pd,'128','RAID6','Uefi','RFS')'''

    def ISCSI(self, mode, bSource, ipVer, ipType):
        self.fd.write('<test name = "install_ISCSI_%s_%s_%s_%s">\n' % (mode, bSource, ipVer, ipType))
        self.fd.write('<parameters>\n')
        
        self.getPXENIC()
        self.getIscsiNIC()
        self.getFcoeNIC()
        self.otherNIC()
        self.getRAIDController()
        self.fd.write('<initiator>iqn.2000-04.com.iscsi:automation</initiator>\n')
        self.fd.write('<target_iqn>iqn.2001-05.com.equallogic:0-8a0906-91ca2ae0a-3560a30b37755066-automation</target_iqn>\n')
        if ipVer == 'IPv4':
            self.fd.write('<target_ip>100.98.4.10</target_ip>\n')
            if ipType == 'STATIC':
                self.fd.write('<initiator_ip>100.98.4.5</initiator_ip>\n')
                self.fd.write('<initiator_subnet>255.255.252.0</initiator_subnet>\n')
                self.fd.write('<initiator_gateway>100.98.4.1</initiator_gateway>\n')
                self.fd.write('<initiator_dns>100.98.4.4</initiator_dns>\n')
        else:
            self.fd.write('<target_ip>fc00::3</target_ip>\n')
            if ipType == 'STATIC':
                self.fd.write('<initiator_ip>fc00::7</initiator_ip>\n')
                self.fd.write('<initiator_subnet>fc00::0</initiator_subnet>\n')
                self.fd.write('<initiator_gateway>fc00::1</initiator_gateway>\n')
                self.fd.write('<initiator_dns>fc00::1</initiator_dns>\n')
        
        self.fd.write('</parameters>\n')
        self.wTestCases('/CoreOS/beaker/Sanity/var-log-analysis', ['LOG_FILE'], ['/var/log/messages'])
        self.wTestCases('/installation/beaker/Install/check-installation', ['INSTALL_MODE_CHECK_VALUE'], ['ISCSI'])
        self.fd.write('</test>\n')
    def ISCSITests(self):
        self.ISCSI('Bios', 'PXE', 'IPv4', 'DHCP')
        self.ISCSI('Uefi', 'PXE', 'IPv4', 'DHCP')
        self.ISCSI('Bios', 'PXE', 'IPv6', 'DHCP')
        self.ISCSI('Uefi', 'PXE', 'IPv6', 'DHCP')
        self.ISCSI('Bios', 'PXE', 'IPv4', 'STATIC')
        self.ISCSI('Uefi', 'PXE', 'IPv4', 'STATIC')
        self.ISCSI('Bios', 'PXE', 'IPv6', 'STATIC')
        self.ISCSI('Uefi', 'PXE', 'IPv6', 'STATIC')
        
        '''self.ISCSI('Bios','RFS','IPv4','DHCP')
        self.ISCSI('Uefi','RFS','IPv4','DHCP')
        self.ISCSI('Bios','RFS','IPv6','DHCP')
        self.ISCSI('Uefi','RFS','IPv6','DHCP')
        self.ISCSI('Bios','RFS','IPv6','STATIC')
        self.ISCSI('Uefi','RFS','IPv6','STATIC')
        self.ISCSI('Bios','RFS','IPv4','STATIC')
        self.ISCSI('Uefi','RFS','IPv4','STATIC')'''
    def FCoE(self, mode, bSource, ipVer, ipType):
        self.fd.write('<test name = "install_FCoE_%s_%s_%s_%s">\n' % (mode, bSource, ipVer, ipType))
        self.fd.write('<parameters>\n')
        self.getPXENIC()
        self.getIscsiNIC()
        self.getFcoeNIC()
        self.otherNIC()
        self.getRAIDController()
        self.fd.write('<FCoE>%s</FCoE>\n' % (self.fcoeNIC))
        self.fd.write('</parameters>\n')
        self.wTestCases('/CoreOS/beaker/Sanity/var-log-analysis', ['LOG_FILE'], ['/var/log/messages'])
        self.wTestCases('/installation/beaker/Install/check-installation', ['INSTALL_MODE_CHECK_VALUE'], ['ISCSI'])
        self.fd.write('</test>\n')
    def FcoETests(self):
        self.FCoE('Bios', 'PXE', 'IPv4', 'DHCP')
        self.FCoE('Uefi', 'PXE', 'IPv4', 'DHCP')
        
    def getSys(self):
        result = self.nic.conn.enumerate('dcim_systemview')
        if result:
            m = result['System.Embedded.1']['Model']
            model = m.replace('PowerEdge', '').strip()
            tag = result['System.Embedded.1']['ServiceTag']
            return "%s-%s" % (model, tag)
        else:
            logging.error("enumation failed result:")
            logging.debug(result)
            return False
        
    def genTest(self):
        
        self.fd.write(' <test name="general">\n')
        self.fd.write('<parameters>\n')
        '''self.nic.wsman.enumerate('DCIM_SystemView')

        m=self.nic.wsman.parseValueFromXML('Model')
        if len(m) ==2:
            model=m[1].replace('PowerEdge','').strip()
        else:
            model=m[0].replace('PowerEdge','').strip()
        t=self.nic.wsman.parseValueFromXML('ServiceTag')
        tag=t[0].strip()'''
        
        self.fd.write('<system>%s</system>\n' % (self.systemName))
        self.fd.write('<idrac>%s</idrac>\n' % (self.server_ip))
        self.fd.write('<kopt>ignore_loglevel</kopt>\n')
        self.fd.write('<family>%s</family>\n' % (self.OSFamily))
        self.fd.write('<distro>%s</distro>\n' % (self.OSDistro))
        self.fd.write('<server>172.16.64.1</server>\n<user>automation</user>\n<password>automation</password>\n<isoname>RHEL-7.0 Server.x86_64</isoname>\n')
        self.fd.write('<isodst>/var/ftp/pub/automation/install/rhel71_automation.iso</isodst>\n \
                                <isosrc>/var/ftp/pub/redhat/RHEL7/7.1/Server/x86_64/iso/RHEL-7.1-20150219.1-Server-x86_64-dvd1.iso  </isosrc> \n \
                                <kspath>/var/ftp/pub/automation/install/RHEL7.1_cfg/ksCdromRh.cfg</kspath> \n \
                                <isolinuxpath>/var/ftp/pub/automation/install/RHEL7.1_cfg/isolinux.cfg</isolinuxpath> \n ')
        
        self.fd.write('</parameters>\n')
        self.fd.write(' </test>\n')
        

    def writeXML(self):
        pass
        '''
        self.fd.write('<systems>\n')
        system_name = self.systemName
        self.fd.write('<system name="%s">\n' % (system_name))
        self.fd.write('<tests>\n')
        self.genTest()
        self.RAIDTests()
        self.ISCSITests()
        self.fd.write('</tests>\n')
        self.fd.write('</system>\n')
        self.fd.write('</systems>\n')'''

    def wTestCases(self, name, params, values):
        self.fd.write('<testcase name="%s">\n' % (name))
        if params != []:
            for i in range(0, len(params)):
                self.fd.write('\t<%s>%s</%s>\n' % (params[i], values[i], params[i]))
                          
        self.fd.write('</testcase>\n')
        
        
p = systemScan()
# p.iscsiSupport()
# p.fcoeSupport()
# p.pxeSupport()
p.writeXML()
