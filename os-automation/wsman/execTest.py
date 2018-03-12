#***************************************************************************
# Test Case Name   : Lib_osinstall
# Description    : General library to install os on SUTs
# Author         : Shilpa
# Created        : 2015-02-27
#***************************************************************************

#*************************General python Imports****************************
import os
import sys
import time
import subprocess
import re
#******************************Local Imports********************************
# from testconfig import testconfig
from w_OSDeployment_mgmt import wsman_OSDeployment
from w_bios_mgmt import wsman_BIOSMgmt
from w_nic_mgmt import wsman_NICMgmt
from w_raid_mgmt import wsman_RAID
from w import wsman
from command import Command
import logging
from w_job_mgmt import wsman_jobMgmt
#*******************************Main Script*********************************
class execTest:
    def __init__(self, install_tests, tests, conf, system):

        for test in install_tests:
            self.testcases = tests
            self.testName = test
            self.hwConf = conf.getParameters1(system, test)
            self.param = conf.getParameters1(system, 'general')
            self.ip = self.param['idrac']
            self.server = self.param['system']
            self.family = self.param['family']
            self.distro = self.param['distro']
            self.kopt = self.param['kopt']
            self.logFile = "%s_%s" % (system, test)
            self.conn = wsman(self.ip)
            self.wsman = wsman_OSDeployment(self.conn)
            self.jobList = []
            self.bios = wsman_BIOSMgmt(self.conn)
            self.job = wsman_jobMgmt(self.conn)
            self.raid = wsman_RAID(self.conn)
            self.nic = wsman_NICMgmt(self.conn)
            n = self.testName.split('_')
            if n[0] == 'install':
                
                logging.debug('Starting test:%s' % (self.testName))
                for t in self.testcases.keys():
                    logging.debug('\tSubtest:%s' % (t))
                logging.debug('Hardware configuration')
                for h in self.hwConf.keys():
                    logging.debug('%s:%s' % (h, self.hwConf[h]))
                                  
                logging.debug('Other configuration')
                for h in self.param.keys():
                    logging.debug('%s:%s' % (h, self.param[h]))
                    
                if not self.installTests():
                    logging.error('Error test failed exiting')
                    # sys.exit() # need to uncomment 
                
    def schduleJobs(self):
        xid = []
        if len(self.jobList) > 0:
            for i in self.jobList:
                if i == 'RAID':
                    c = self.raid.getControllers()
                    xid.append(self.job.CreateJob(jobType='ConfigRAID:%s' % (c[0])))
                elif i == 'BIOS':
                    tmp = self.job.CreateJob(jobType='ConfigBIOS:BIOS.Setup.1-1')
                    xid.append(tmp)
                elif i == 'NIC':
                    xid.append(self.job.CreateJob(jobType='ConfigNIC:%s' % self.hwConf['PXE']))
                    xid.append(self.job.CreateJob(jobType='ConfigNIC:%s' % self.hwConf['ISCSI']))
                    
            # self.job.SetupJobQueue(xid)

        
    def PERCEnable(self, Enable=True):
        if Enable:
            value = 'Enabled'
        else:
            value = 'Disabled'
        if 'Slot' in self.hwConf['PERC']:
            slot = self.hwConf['PERC'].replace('RAID.', '').split('-')[0].replace('.', '')
            if self.bios.getSlotStatus(slot) != value:
                logging.debug("Enabling PERC slot")
                if self.bios.enableSlot(slot, value):
                    return self.bios.creatAndmonitorJob('TIME_NOW')
                    
                
        if 'Integrated' in self.hwConf['PERC']:
            if self.bios.getIntegratedRaidControllerStatus() != value:
                logging.debug("Enabling Integrated PERC Controller")
                if self.bios.enableRaidController(value):
                    return self.bios.creatAndmonitorJob('TIME_NOW')
                    
        return False
                
    def RAIDConfig(self):
        logging.debug("Configuring RAID")
        self.PERCEnable()
        n = self.testName.split('_')
        vd = self.raid.getVirtualDisk()
        if vd:
            if self.hwConf['level'] != self.raid.getRaidType(vd[0]):
                self.raid.deleteAllVD()
                logging.debug('deleting vd:%s' % (vd[0]))
                self.raid.creatAndmonitorJob(self.hwConf['PERC'])
                logging.debug("Creating RAID level:%s" % (self.hwConf['level']))
                if not self.raid.createVirtualDisk(self.hwConf['disk'].split(','), self.hwConf['level'], self.hwConf['spandepth'], self.hwConf['spanlength'], n[1]):
                    logging.error("RAID Creation Failed")
                    return False
                else:
                    self.raid.creatAndmonitorJob(self.hwConf['PERC'], 'TIME_NOW')
            else:
                logging.debug("already  RAID configured")
        logging.info("PERC configuration success ")
        return True

        
    def ISCSIConfig(self):
        offload = False
        self.PERCEnable(False)
        logging.info("Configuring %s for ISCSI" % (self.hwConf['ISCSI']))
        n = self.testName.split('_')
       
        att = {}
        nic = self.hwConf['ISCSI']
        if n[2] == "Bios":
        
            if len(n) >= 7 and n[6] == 'offload':
                if not self.nic.getiSCSIOffloadSupport(nic):
                    logging.error("ISCSI Offload not supported")
                    return False
                
                else:
                    logging.debug("ISCSI offload supported")
                    offload = True
            if not self.nic.getiSCSIBootSupport(nic):
                logging.error("ISCSI boot is not supported")
                return False
            else:
                logging.info('%s supports iSCSI boot' % (nic))
                
            if self.nic.getLinkStatus(nic) != 'Connected' :
                logging.error("Cable not Connected to port")
                return False
            else:
                logging.info('%s cable connected' % (nic))
            
            if self.nic.getLegacyBootProto(nic) != 'iSCSI':
                att['AttributeName'] = 'LegacyBootProto'
                att['AttributeValue'] = 'iSCSI'
            else:
                logging.info('already LegacyBootProto:iSCSI')
            
            name = ['IscsiViaDHCP', 'ChapAuthEnable', 'FirstHddTarget', 'IscsiTgtBoot',
                  'IpVer', 'ConnectFirstTgt', 'VLanMode', 'FirstTgtTcpPort', 'FirstTgtBootLun',
                  'IscsiInitiatorName', 'FirstTgtIpAddress', 'FirstTgtIscsiName']
            
            value = ['Disabled', 'Disabled', 'Enabled', 'OneTimeDisabled',
                   '%s' % n[4], 'Enabled', 'Disabled', '3260', '0',
                   str(self.hwConf['initiator']), str(self.hwConf['target_ip']), str(self.hwConf["target_iqn"])]
            if offload == True:
                name.append('WinHbaBootMode')
                value.append('Enabled')
                logging.debug("Enabling  HBA boot Mode")
            else:
                # name.append('WinHbaBootMode')
                # value.append('Disabled')
                print "disabling HBA boot Mode"
            if n[5] == 'DHCP' :
                name.append('TcpIpViaDHCP')
                value.append('Enabled')
                logging.debug("TCP/IP via DHCP")
            elif n[5] == 'STATIC':
                logging.debug("TCP/IP via STATIC IP")
                name.append('TcpIpViaDHCP')
                value.append('Disabled')
                name.append('IscsiInitiatorIpAddr')
                value.append(str(self.hwConf['initiator_ip']))
                name.append('IscsiInitiatorSubnet')
                value.append(str(self.hwConf['initiator_subnet']))
                name.append('IscsiInitiatorGateway')
                value.append(str(self.hwConf['target_gateway']))
                name.append('IscsiInitiatorPrimDns')
                value.append(str(self.hwConf['target_dns']))
            for i in range(0, len(name)):
                if 'AttributeName' in att:
                    att['AttributeName'] = att['AttributeName'] + ',' + name[i]
                    att['AttributeValue'] = att['AttributeValue'] + ',' + value[i]
                else:
                    att['AttributeName'] = name[i]
                    att['AttributeValue'] = value[i]
            if self.nic.SetAttributes(nic, att['AttributeName'], att['AttributeValue']):
                
                self.nic.creatAndmonitorJob(nic, 'TIME_NOW')
                # self.jobList.append('NIC')
        
        if n[2] == 'Uefi':  
            self.jobList.append('BIOS') 
            self.bios.SetAttribute('IscsiDev1EnDis', 'Enabled')
            self.bios.SetAttribute('IscsiDev1Con1EnDis', 'Enabled')
            self.bios.SetAttribute('IscsiInitiatorName', '%s' % (self.hwConf['initiator']))
            self.bios.SetAttribute('IscsiDev1con1Auth', 'None')
            self.bios.SetAttribute('IscsiDev1Con1Timeout', '10000')    
            self.bios.SetAttribute('IscsiDev1Con1VlanEnDis', 'Disabled')
            self.bios.SetAttribute('IscsiDev1Con1Interface', '%s' % (self.hwConf['ISCSI']))
            if n[4] == 'IPv4':
                self.bios.SetAttribute('IscsiDev1Con1Protocol', 'IPv4')
            else:
                self.bios.SetAttribute('IscsiDev1Con1Protocol', 'IPv6')
            self.bios.SetAttribute('IscsiDev1Con1TgtDhcpEnDis', 'Disabled')
            self.bios.SetAttribute('IscsiDev1Con1VlanEnDis', 'Disabled')
            self.bios.SetAttribute('IscsiDev1Con1Lun', '0')
            self.bios.SetAttribute('IscsiDev1Con1Port', '3260')
            self.bios.SetAttribute('IscsiDev1Con1Retry', '3')
            self.bios.SetAttribute('IscsiDev1Con1TargetName',
                                   '%s' % (self.hwConf["target_iqn"]))
            self.bios.SetAttribute('IscsiDev1Con1TargetIp',
                                   '%s' % (self.hwConf['target_ip']))
            if n[5] == 'DHCP':
                self.bios.SetAttribute('IscsiDev1Con1DhcpEnDis', 'Enabled')
            if n[5] == 'STATIC':
                self.bios.SetAttribute('IscsiDev1Con1DhcpEnDis', 'Disabled')
                self.bios.SetAttribute('IscsiDev1Con1Ip', '%s' % (self.hwConf['initiator_ip']))
                self.bios.SetAttribute('IscsiDev1Con1Gateway', '%s' % (self.hwConf['target_gateway']))
                self.bios.SetAttribute('IscsiDev1con1Mask', '%s' % (self.hwConf['initiator_subnet']))
            self.bios.creatAndmonitorJob('TIME_NOW')
        return True
    def FCConfig(self):
        print "Configuring FC"
        pass
    def FCoEConfig(self):
        print "Configuring FCoE"
        pass
    def PXEConfig(self):
        logging.debug("configuring PXE")
        n = self.testName.split('_')
        
        if n[2] == "Bios":
            if self.nic.getPXEBootSupport(self.hwConf['PXE']):
                logging.info("%s is capable of PXE" % (self.hwConf['PXE']))
                if self.nic.getLegacyBootProto(self.hwConf['PXE']) != 'PXE':
                    self.nic.SetAttribute(self.hwConf['PXE'], 'LegacyBootProto' , 'PXE')
                    if 'NICS' in self.hwConf:
                        ports = self.hwConf['NICS']
                        NoneCheck = False
                        for port in ports.split(','):
                            port = port.strip()
                            if self.nic.getLegacyBootProto(port) == 'NONE':
                                logging.debug("port %s already LegacyBootProto=NONE" % port)
                                continue
                            else:
                                self.nic.SetAttribute(port, 'LegacyBootProto' , 'NONE')
                                NoneCheck = True
            else:
                print "%s already PXE mode" % (self.hwConf['PXE'])
        if n[2] == "Uefi":
            self.bios.SetAttribute('PxeDev1EnDis', 'Enabled')
            self.bios.SetAttribute('PxeDev1Interface', '%s' % (self.hwConf['PXE']))
            self.bios.SetAttribute('PxeDev1VlanEnDis', 'Disabled')
            if n[3] == 'PXE4':
                self.bios.SetAttribute('PxeDev1Protocol', 'IPv4')
            elif n[3] == 'PXE6':
                self.bios.SetAttribute('PxeDev1Protocol', 'IPv6')
            self.bios.creatAndmonitorJob('TIME_NOW')
            
                

            
        if n[1] == 'ISCSI':
            f = ''
            s = ''
            bootSource = self.bios.getBootSourceInstanceID(n[2])
            if n[2] == "Uefi":
                for i in bootSource:
                    if 'Unknown' in i:
                        bootSource.remove(i)
            for i in bootSource:
                if self.hwConf['ISCSI'] in i or 'IscsiDevice' in  i:
                    f = i  
                elif self.hwConf['PXE'] in i or 'PxeDevice' in i :
                    s = i
                else:
                    continue  
            jx = ""
            if s:
                bootSource.remove(s)
                jx = '%s' % (s)
                
            if f and s:
                bootSource.remove(f)
                jx = '%s,%s' % (f, jx)
            elif f and not s:
                bootSource.remove(f)
                jx = '%s' % (f)
            if bootSource != []:
                j = ','.join(bootSource)
                if re.match('^,,', j, re.I | re.M):
                    j = j.replace(',,', '')
                else:
                    j = j.replace(',,', ',')
                if re.match('^,', j, re.I | re.M):
                    j = j.replace(',', '')
                
                j = '%s,%s' % (jx, j)
            else:
                j = jx
            print j
            if self.bios.ChangeBootOrderByInstanceID('typeInstance', '%s' % (j)):
                if self.bios.getPendingAssignedSequence():
                    self.bios.creatAndmonitorJob('TIME_NOW')
                return True
            else:
                logging.error('Failed to change boot order for instance IDs:%s' % (j))     
                return False
        else:
            self.bios.setOneTimeBoot(self.hwConf['PXE'])
        return True
    def RFSConfig(self):
        print "Configuring RFS"
        self.createISOWithKS()
        osdeploy = wsman_OSDeployment(self.ip)
        isoName = os.path.basename(self.param['isodst'])
        isoPath = os.path.dirname(self.param['isodst'])
        if osdeploy.GetRFSISOImageConnectionInfo() != 0:
            osdeploy.DisconnectRFSISOImage()
        if not osdeploy.ConnectRFSISOImage(self.param['server'], isoPath, isoName):
            print "Not able to connect ISO in RFS"
            return False
        return True
    def bootFromHDD(self):
        bios = wsman_BIOSMgmt(self.ip)
        vds = bios.getBootSourceInstanceID()
        for v in vds:
            if 'BCV' in v:
                self.configFirstBoot(v, '0')
        

    #
    #                        MAIN  FUNCTION
    #
    def installTests(self):
        n = self.testName.split('_')
        mediaOptions = {'RAID': self.RAIDConfig, 'ISCSI': self.ISCSIConfig, 'FC' :self.FCConfig, 'FCoE' : self.FCoEConfig}
        
        installSource = {'PXE':self.PXEConfig, 'RFS':self.RFSConfig}
        if not  self.bios.setBIOSMode(n[2]):
            print "Error: install Mode setting failed"
            return False
        
        if 'RAID' in n[1] :
            if not mediaOptions['RAID']():
                print "Error: install media setting failed"
                return False
        
        m = ''.join(i for i in n[1] if i.isalpha())
        self.submitJobToBeaker()
        if not  mediaOptions[m]():
            print "Error:setting install DST failed"
            return False
        
        installSource[n[3]]()
        print self.jobID
        os.system('bkr job-watch %s' % (self.jobID))
        return True
        
    def configISCSI(self):
        print "Configuring %s for ISCSI" % (self.hwConf['ISCSI'])
        
        n = self.testName.split('_')
        nic_obj = wsman_NICMgmt(self.ip)
        att = {}
        nic = self.hwConf['ISCSI']

        if not nic_obj.getiSCSIBootSupport(nic):
            print "ISCSI boot is not supported"
            return False
        elif nic_obj.getLinkStatus(nic) != 'Connected' :
            print "Cable not Connected to port"
            return False
        
        elif nic_obj.getLegacyBootProto(nic) != 'iSCSI':
            att['AttributeName'] = 'LegacyBootProto'
            att['AttributeValue'] = 'iSCSI'
        
        name = ['IscsiViaDHCP', 'ChapAuthEnable', 'FirstHddTarget', 'IscsiTgtBoot',
              'IpVer', 'ConnectFirstTgt', 'VLanMode', 'FirstTgtTcpPort', 'FirstTgtBootLun',
              'IscsiInitiatorName', 'FirstTgtIpAddress', 'FirstTgtIscsiName']
        
        value = ['Disabled', 'Disabled', 'Enabled', 'OneTimeDisabled',
               '%s' % n[4], 'Enabled', 'Disabled', '3260', '0',
               str(self.hwConf['initiator']), str(self.hwConf['target_ip']), str(self.hwConf["target_iqn"])]
         
        if n[5] == 'DHCP':
            
            name.append('TcpIpViaDHCP')
            value.append('Enabled')
        elif n[5] == 'STATIC':
            name.append('TcpIpViaDHCP')
            value.append('Disabled')
            name.append('IscsiInitiatorIpAddr')
            value.append(str(self.hwConf['initiator_ip']))
            
            name.append('IscsiInitiatorSubnet')
            value.append(str(self.hwConf['initiator_subnet']))
        
            name.append('IscsiInitiatorGateway')
            value.append(str(self.hwConf['target_gateway']))
            
            name.append('IscsiInitiatorPrimDns')
            value.append(str(self.hwConf['target_dns']))
        for i in range(0, len(name)):
            if 'AttributeName' in att:
                att['AttributeName'] = att['AttributeName'] + ',' + name[i]
                att['AttributeValue'] = att['AttributeValue'] + ',' + value[i]
            else:
                att['AttributeName'] = name[i]
                att['AttributeValue'] = value[i]
                
        if nic_obj.SetAttributes(nic, att):
            if nic_obj.CreateTargetedConfigJob(self.hwConf['ISCSI']) == "4096":
                return nic_obj.monitorJob()
            else:
                logging.error('Error in creating config job')
                return  False
        else:
            logging.error('Error in setting attribute')
            return False
    def configFirstBoot(self, ins, pos, job):
        n = self.testName.split('_')
        bios = wsman_BIOSMgmt(self.conn)
        bios.setOneTimeBoot(ins)
        
    def setMedia(self):  # PERC   ISCSI FC FCOE onboardSATA
        n = self.testName.split('_')
        # configure PERC card for RAID
        if n[0] == 'install' and  'RAID' in n[1]:
            print 'RAID INSTALL'
            bios = wsman_BIOSMgmt(self.ip)
            bios.enableSlot(self.hwConf['PERC'])
            raid = wsman_RAID(self.ip)
            raid.deleteAllVD()
            raid.createVirtualDisk(self.hwConf['disk'].split(','), self.hwConf['level'], self.hwConf['spandepth'], self.hwConf['spanlength'], n[1])
            print "PERC configuration success "
            vds = bios.getBootSourceInstanceID()
            for v in vds:
                if 'BCV' in v:
                    self.configFirstBoot(v, '0')
        elif n[0] == 'install' and  'ISCSI' in n[1]:
            print 'ISCSI INSTALL'
            bios = wsman_BIOSMgmt(self.ip)
            bios.enableSlot(self.hwConf['PERC'], 'Disabled')
            self.configISCSI()
            self.configFirstBoot(self.hwConf['ISCSI'], '0')
                
    def configureNetwork(self):  
        nic = wsman_NICMgmt(self.ip)
        if nic.getPXEBootSupport(self.hwConf['PXE']):
            if nic.getLegacyBootProto(self.hwConf['PXE']) != 'PXE':
                nic.SetAttribute(self.hwConf['PXE'], 'LegacyBootProto' , 'PXE')
                ports = self.hwConf['NICS']
                for port in ports.split(','):
                    nic.SetAttribute(port, 'LegacyBootProto' , 'NONE')
                nic.CreateTargetedConfigJob(self.hwConf['PXE'])
                nic.monitorJob()
        self.configFirstBoot(self.hwConf['PXE'], '0')
        return

    def setbootMode(self):  # UEFI BIOS
        n = self.testName.split('_')
        configJobRequired = False
        bios = wsman_BIOSMgmt(self.ip)
        if bios.getbootMode() != n[2]:
            bios.SetAttribute('BootMode', n[2])
            configJobRequired = True
        if n[3] == 'RFS' or n[3] == 'VM':
            source = 'Optical.iDRACVirtual'
            if n[2] == 'Bios':
                bootsource = 'IPL'
            elif n[2] == 'Uefi' :
                bootsource = 'UEFI'
            bootlist = bios.getBootSourceInstanceID()
            # filtering bootsource BIOS or UEFI
            bootlist = [x for x in bootlist if bootsource in x]
            for i in bootlist:
                if source in i:
                    bios.oneTimeBoot(i)
                    bios.creatAndmonitorJob()
                    break
        elif n[0] == 'install' and n[3] == 'PXE' :
            if configJobRequired:
                bios.creatAndmonitorJob()
            self.configureNetwork()
            self.submitJobToBeaker()


    def submitJobToBeaker(self):  
        tsc = ""
        x = ""
        for p in self.testcases:
            
            if tsc == "":
                
                tsc = '--task' + ' ' + p
            else:
                tsc = tsc + ' ' + '--task' + ' ' + p
                
            if ':' in self.testcases[p]:
                name = self.testcases[p].split(':')[0]
                val = self.testcases[p].split(':')[1]
                if x == "":
                    x = '--taskparam' + '=' + name + '=' + val
                else:
                    x = x + ' ' + '--taskparam' + '=' + name + '=' + val
                
            tsc = tsc + ' ' + x
        logging.debug('**Starting beaker job')
        cmd = Command('bkr workflow-simple  --kernel-options="%s"   --family=%s --distro="%s" --arch=x86_64 --variant=Server --task /distribution/install  --machine=%s --method=http --whiteboard=%s_%s %s' % (self.kopt, self.family, self.distro, self.server, self.testName, self.server, tsc))
        cmd.run()
        self.jobID = cmd.output[0].split('[')[1].replace('\'', '').replace(']', '')
        
        
    def setBootProtocol(self):  # PXE RFS VM
        print "here inside method"
        self.attacheInstallationMedia()
        if self.bproto == "PXE":
            self.wsman.BootToPXE()

        else:
            # attaching iso for RFS and VM
            self.attacheInstallationMedia()


    def attacheInstallationMedia(self):
        print "In side "
        self.createISOWithKS()
        isoName = os.path.basename(self.param['isodst'])
        isoPath = os.path.dirname(self.param['isodst'])
        if self.bproto == "VM":
            print self.wsman.BootToNetworkISO(self.param['server'], isoPath, isoName)
            print self.wsman.GetAttachStatus()
        elif self.bproto == "RFS":
            if self.wsman.GetRFSISOImageConnectionInfo() != 0:
                self.wsman.DisconnectRFSISOImage()
            if not self.wsman.ConnectRFSISOImage(self.param['server'], isoPath, isoName):
                print "Not able to connect ISO in RFS"
                return False
        else:
            if self.wsman.GetRFSISOImageConnectionInfo() != 0:
                self.wsman.DisconnectRFSISOImage()
            if not self.wsman.ConnectRFSISOImage(self.param['server'], isoPath, isoName):
                print "Not able to connect ISO in RFS"
                return False
        return True

    def createISOWithKS(self):
        print "inside createISO"
        scriptFile = '/usr/share/v7/lib/v7/createISO.sh'
        # self.getconfig()
        src = re.escape(self.param['isosrc'])
        cmd = Command('sed -i "s/^SRC_ISO.*$/SRC\_ISO\=\\"%s\\"/" %s' % (src, scriptFile))
        cmd.echo()
        
        src = re.escape(self.param['isodst'])
        cmd = Command('sed -i "s/^DST_ISO.*$/DST\_ISO\=\\"%s\\"/" %s' % (src, scriptFile))
        cmd.echo()
        
        src = re.escape(self.param['kspath'])
        cmd = Command('sed -i "s/^PATH_KS.*$/PATH\_KS\=\\"%s\\"/" %s' % (src, scriptFile))
        cmd.echo()
          
        src = re.escape(self.param['isolinuxpath'])
        cmd = Command('sed -i "s/^PATH_ISOLINUX.*$/PATH\_ISOLINUX\=\\"%s\\"/" %s' % (src, scriptFile))
        cmd.echo()
        
        src = re.escape(self.param['isoname'])
        cmd = Command('sed -i "s/^ISO_NAME.*$/ISO\_NAME\=\\"%s\\"/" %s' % (src, scriptFile))
        cmd.echo()
        
        cmd = Command('/usr/share/v7/lib/v7/createISO')
        cmd.echo()
        print "ISO done"



