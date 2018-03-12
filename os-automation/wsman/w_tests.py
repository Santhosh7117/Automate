from w import wsman
from w_bios_mgmt import wsman_BIOSMgmt
from w_lc_mgmt import wsman_LCMgmt
from w_nic_mgmt import *
from w_raid_mgmt import *
from w_OSDeployment_mgmt import wsman_OSDeployment
from w_fc_mgmt import w_fc_mgmt
import unittest
import time
import logging
from w_inventory import wsman_inventory
from django.conf.global_settings import LOGGING_CONFIG
className='dcim_biosenumeration'
instanceID='BIOS.Setup.1-1:BootMode'
AttributeName='BootMode'
#w=wsman('100.98.5.170')
w=wsman('100.98.4.77')
i=wsman_inventory(w)
b=wsman_BIOSMgmt(w)
n=wsman_NICMgmt(w)
o=wsman_OSDeployment(w)
r=wsman_RAID(w)
fc=w_fc_mgmt(w)
lc=wsman_LCMgmt(w)

systemName='M830'



class cm_test(unittest.TestCase):
    @unittest.skip("demonstrating skipping")
    def test_get_inventory(self):
        print i.get_inventory()
        print i.installFromURI()
    @unittest.skip("demonstrating skipping")
    def test_enumarate(self):
        #self.assertIn(instanceID, w.enumerate(className))
         w.enumerate(className)
    @unittest.skip("demonstrating skipping")
    def test_get(self):
        self.assertIn(instanceID, w.get('dcim_lcenumeration','lifecyclecontrollerstate'))
    @unittest.skip("demonstrating skipping")
    def test_invoke(self):
        self.assertTrue(instanceID, w.invoke('dcim_biosservice', 'setattribute', {'Target':'BIOS.Setup.1-1','AttributeName':'BootMode','AttributeValue':'Bios'}))
    

        
    #LC MGMT
    @unittest.skip("demonstrating skipping")
    def test_ExportSystemConfiguration(self):
        fName='R730_G471CD2_UEFI_ISCSI_PXEv4_DHCP__bcm57810s.xml'
        #fName='R930_CG8CH62_UEFI_RAID0_PXEv4.xml'
        jobid=lc.ExportSystemConfiguration(IPAddress='100.98.4.4',ShareName='public/test',ShareType='2',FileName=fName)
        lc.monitorJob(jobid)
    @unittest.skip("demonstrating skipping")
    def test_ExportFactoryConfiguration(self):
        pass
    
        
    #@unittest.skip("demonstrating skipping")
    def test_ImportSystemConfiguration(self):
        fName='R730_G471CD2_BIOS_ISCSI_PXEv4_DHCP__bcm57810s.xml'
        jobid=lc.ImportSystemConfiguration(IPAddress='100.98.4.4',ShareName='public/test',ShareType='2',FileName=fName)
        #lc.CreateConfigJob()
        lc.monitorJob(jobid)
        
    @unittest.skip("demonstrating skipping")
    def test_BackupImage(self):
        fName='backupImage.xml'
        self.assertTrue(lc.BackupImage(IPAddress='100.98.4.4',ShareName='public/test',ShareType='2',ImageName=fName))
    @unittest.skip("demonstrating skipping")
    def test_RestoreImage(self):
        fName='backupImage.xml'
        self.assertTrue(lc.RestoreImage(IPAddress='100.98.4.4',ShareName='public/test',ShareType='2',FileName=fName))
        
    @unittest.skip("demonstrating skipping")
    def test_ExportHWInventory(self):
        self.assertTrue(lc.ExportHWInventory())

    #
    #BIOS MGMT
    @unittest.skip("demonstrating skipping")
    def test_getBootSourcesInstanceID(self):
        self.assertTrue(b.getBootSourcesInstanceID())
    @unittest.skip("demonstrating skipping")
    def test_getIntegratedNetwork1Status(self):
        self.assertTrue(b.getIntegratedNetwork1Status())
        
    @unittest.skip("demonstrating skipping")
    def test_getbootMode(self):
        self.assertIn(b.getbootMode(), ['Bios','Uefi'])
    @unittest.skip("demonstrating skipping")
    def test_getIntegratedRaidControllerStatus(self):
        self.assertIn(b.getIntegratedRaidControllerStatus(), ['Enabled','Disabled'])
    @unittest.skip("demonstrating skipping")
    def test_getSlotStatus(self):
        self.assertTrue(b.getSlotStatus('Slot1'))
        
    @unittest.skip("demonstrating skipping")
    def test_SetAttribute(self):
        self.assertTrue(b.SetAttribute('BootMode','Bios'))
        
    @unittest.skip("demonstrating skipping")
    def test_enableSlot(self):
        self.assertTrue(b.enableSlot('Slot1'))
        
    @unittest.skip("demonstrating skipping")
    def test_enableSlot_Disable(self):
        self.assertTrue(b.enableSlot('Slot1',status='Disabled'))
    @unittest.skip("demonstrating skipping")
    def test_enableSlots(self):
        self.assertTrue(b.enableSlots('Slot1,Slot2'))
    @unittest.skip("demonstrating skipping")
    def test_enableRaidController(self):
        self.assertTrue(b.enableRaidController())
        
    @unittest.skip("demonstrating skipping")
    def test_SetAttributes(self):
        self.assertTrue(b.SetAttributes('BootMode,LogicalProc','Bios,Enabled'))
    @unittest.skip("demonstrating skipping")
    def test_createTargetedConfigJob(self):
        self.assertTrue(b.SetAttribute('BootMode','Bios'))
        self.assertTrue(b.CreateTargetedConfigJob())
        
    @unittest.skip("demonstrating skipping")
    def test_DeletePendingConfiguration(self):
        self.assertTrue(b.SetAttribute('BootMode','Bios'))
        self.assertTrue(b.CreateTargetedConfigJob())
        self.assertTrue(b.DeletePendingConfiguration())
    @unittest.skip("demonstrating skipping")
    def test_CreateTargetedConfigJob(self):
        self.assertTrue(b.SetAttribute('BootMode','Bios'))
        self.assertTrue(b.creatAndmonitorJob())
    @unittest.skip("demonstrating skipping")
    def test_getBootStateEnabled(self):
        src=b.getBootSourcesInstanceID()
        for i in src:
            self.assertIn(b.getBootStateEnabled(i),['0','1'])
    @unittest.skip("demonstrating skipping")
    def test_enum(self):
        result=b.conn.enumerate('dcim_biosenumeration')
        #result=b.conn.enumerate('dcim_biosstring')
        #result=b.conn.enumerate('dcim_biosinteger')
        #result=b.conn.enumerate('dcim_biosinteger')
        for i in result.keys():
            #print i
            if result[i]['GroupID'] == 'IntegratedDevices':
                print i
            if 'pxe' in i:
                
                print '*****'
    #
    # NIC MGMT
    #
    
    @unittest.skip("demonstrating skipping")
    def test_getAllNIC(self):
        #print n.getAllNIC()
        self.assertTrue(n.getAllNIC())
    @unittest.skip("demonstrating skipping")
    def test_getFCoEOffloadSupport(self):
        nics=n.getAllNIC()
        self.assertIn(n.getFCoEOffloadSupport(nics[0]),['Available','Unavailable'])
    @unittest.skip("demonstrating skipping")
    def test_getiSCSIOffloadSupport(self):
        nics=n.getAllNIC()
        self.assertIn(n.iSCSIOffloadSupport(nics[0]),['Available','Unavailable'])
    @unittest.skip("demonstrating skipping")
    def test_getiSCSIBootSupport(self):
        nics=n.getAllNIC()
        self.assertIn(n.getiSCSIBootSupport(nics[0]),['Available','Unavailable'])
    @unittest.skip("demonstrating skipping")
    def test_getPXEBootSupport(self):
        nics=n.getAllNIC()
        self.assertIn(n.getPXEBootSupport(nics[0]),['Available','Unavailable'])
    @unittest.skip("demonstrating skipping")
    def test_getFCoEBootSupport(self):
        nics=n.getAllNIC()
        self.assertIn(n.getFCoEBootSupport(nics[0]),['Available','Unavailable'])
    @unittest.skip("demonstrating skipping")
    def test_getNicPartitioningSupport(self):
        nics=n.getAllNIC()
        self.assertIn(n.getNicPartitioningSupport(nics[0]),['Available','Unavailable'])
    @unittest.skip("demonstrating skipping")
    def test_dhcp(self):
        result=n.conn.enumerate('dcim_nicenumeration')
        for i in result.key():
            print i
    @unittest.skip("demonstrating skipping")
    def test_FCoEConfig(self):
            
        nic='NIC.Slot.2-2-1'
        ''' if n.getLinkStatus(nic) == 'Connected' and n.getFCoEBootSupport(nic) == 'Available' :
            #print n.getNicPartitioningSupport(nic)
            #if not n.getLegacyBootProto(nic) == 'FCoE':
            if not n.SetAttribute(nic, 'LegacyBootProto', 'FCoE'):
                logging.debug('not able to set LegacyBootProto')
            if not n.SetAttribute(nic,'ConnectFirstFCoETarget', 'Enabled'):
                logging.debug('not able to set ConnectFirstFCoETarget')
            if not n.SetAttribute(nic, 'FCoETgtBoot', 'Enabled'):
                logging.debug('not able to set FCoETgtBoot')
            if not n.SetAttribute(nic, 'FirstFCoEWWPNTarget', '50:00:d3:10:01:02:03:39'):
                logging.debug('not able to set FirstFCoEWWPNTarget')
            if not n.SetAttribute(nic, 'FirstFCoEFCFVLANID', '255'):
                logging.debug('not able to set FirstFCoEFCFVLANID')
             
            result=n.CreateTargetedConfigJob(nic, 'TIME_NOW')
            if result:
                n.monitorJob(result)'''
                
        src=b.getBootSourcesInstanceID()
        print nic
        for i in src:
            print i
            if nic in i:
                
                if b.getBootStateEnabled(instanceID) != '1':
                    logging.debug('enabled for boot')
                else:
                   logging.debug('not enabled for boot') 
                    
        print n.getWWPN(nic)
        
        
        
        
        
        
        
        
    #def test_getWWPN(self):
    #   print fc.getWWPN() 
        
        
        
    
        
    # OS DEPLOYMENT MGMT
    #   
      
    @unittest.skip("demonstrating skipping")  
    def test_GetDriverPackInfo(self):
        print o.GetDriverPackInfo()
        
    @unittest.skip("demonstrating skipping")
    def test_UnpackAndAttach(self):
        self.assertTrue(o.UnpackAndAttach('Red Hat Enterprise Linux 6.7 x64','00000000002200.000000:000'))
    @unittest.skip("demonstrating skipping")
    def test_DetachDrivers(self):
        self.assertTrue(o.DetachDrivers())
    @unittest.skip("demonstrating skipping")
    def test_BootToNetworkISO(self):
        self.assertTrue(o.BootToNetworkISO('172.16.64.1','/var/ftp/pub/automation/RHEL7','rhel7.iso'))
        
    @unittest.skip("demonstrating skipping")    
    def test_DetachISOImage(self):
        self.assertTrue(o.DetachISOImage())
    @unittest.skip("demonstrating skipping")  
    def test_BootToPXE(self):
        self.assertTrue(o.BootToPXE())
    @unittest.skip("demonstrating skipping") 
    def test_BootToHD(self):
        self.assertTrue(o.BootToHD())
    @unittest.skip("demonstrating skipping")
    def test_GetNetworkISOImageConnectionInfo(self):
        self.assertTrue(o.GetNetworkISOImageConnectionInfo())
    @unittest.skip("demonstrating skipping")
    def test_DisconnectNetworkISOImage(self):
        self.assertTrue(o.DisconnectNetworkISOImage())
        
    @unittest.skip("demonstrating skipping")
    def test_ConnectNetworkISOImage(self):
        self.assertTrue(o.ConnectNetworkISOImage('172.16.64.1','/var/ftp/pub/automation/RHEL7','rhel7.iso'))
        time.sleep(10)
        self.assertTrue(o.GetNetworkISOImageConnectionInfo())
        self.assertTrue(o.DisconnectNetworkISOImage())
        
        
    #
    # RAID MGMT
    #    
    def test_test(self):
        args={'VDPropNameArray': 'Initialize,RAIDLevel,VirtualDiskName,SpanDepth,SpanLength', 'PDArray': 'Disk.Bay.0:Enclosure.Internal.0-1:RAID.Integrated.1-1,Disk.Bay.1:Enclosure.Internal.0-1:RAID.Integrated.1-1', 'Target': 'RAID.Integrated.1-1', 'VDPropValueArray': '0,4,RAID1,1,2'}

    @unittest.skip("demonstrating skipping")
    def test_getEnclosure(self):
        print r.getEnclosure()
        self.assertTrue(r.getEnclosure())
    @unittest.skip("demonstrating skipping")
    def test_getControllers(self):
        self.assertTrue(r.getControllers())
    @unittest.skip("demonstrating skipping")   
    def test_getVirtualDisk(self):
        print r.getVirtualDisk()
        self.assertTrue(r.getVirtualDisk())
    @unittest.skip("demonstrating skipping")
    def test_getPhysicalDisks(self):
        self.assertTrue(r.getPhysicalDisks())
    
    @unittest.skip("demonstrating skipping")
    def test_getSupportedRAIDLevels(self):
        c=r.getControllers()
        self.assertTrue(r.getSupportedRAIDLevels(c[0]))
    @unittest.skip("demonstrating skipping")
    def test_getRAIDSupportedDiskProt(self):
        c=r.getControllers()
        self.assertTrue(r.getRAIDSupportedDiskProt(c[0]))
        
    @unittest.skip("demonstrating skipping")   
    def test_getRAIDSupportedInitTypes(self):
        c=r.getControllers()

    @unittest.skip("demonstrating skipping")
    def test_getRAIDloadBalancedMode(self):
        c=r.getControllers()
        self.assertTrue(r.getRAIDloadBalancedMode(c[0]))
    
    @unittest.skip("demonstrating skipping")
    def test_deleteVirtualDisk(self):
        c=r.getControllers()
        print c
        vd = r.getVirtualDisk()
        print vd
        if vd:
            self.assertTrue(r.deleteVirtualDisk(vd[0]))
        r.CreateTargetedConfigJob('RAID.Integrated.1-1', '1', 'TIME_NOW')
    
    @unittest.skip("demonstrating skipping")
    def test_GetDHSDisks(self):
        self.assertTrue(r.GetDHSDisks())
        
    @unittest.skip("demonstrating skipping")
    def test_GetAvailableDisks(self):
        c=r.getControllers()
        print c
        self.assertTrue(r.GetAvailableDisks(c[2]))
    @unittest.skip("demonstrating skipping")
    def test_resetConfig(self):
        c=r.getControllers()
        print c
        print r.resetConfig(c[2])
        print r.CreateTargetedConfigJob(c[2],ScheduledStartTime='TIME_NOW')
    
if __name__ == '__main__':
#        unittest.main()
    logging.basicConfig(level=logging.DEBUG)
    suite = unittest.TestLoader().loadTestsFromTestCase(cm_test)
    unittest.TextTestRunner(verbosity=2).run(suite)
