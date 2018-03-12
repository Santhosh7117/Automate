import pexpect
import sys
from w import wsman
from w_nic_mgmt import wsman_NICMgmt

class zoning:
    def __init__(self):
        self.switchUser='Admin'
        self.switchPassword='P@$$w0rd'
        self.switchIP='10.94.215.215'
        self.conn=wsman('172.16.67.93')
        self.nic=wsman_NICMgmt(self.conn)
          
    def ConfigZone(self,port):
        zoneName='automationZone'
        zoneset='Linux'
        wwpnNIC=self.nic.getWWPN(port)
        wwpnSwitch0='50:00:d3:10:01:02:03:39'
        wwpnSwitch1='50:00:d3:10:01:02:03:3a'
        
        ssh_newkey = 'Are you sure you want to continue connecting'
        
        p=pexpect.spawn('ssh %s@%s'%(self.switchUser,self.switchIP))
        p.logfile = sys.stdout
        i=p.expect([ssh_newkey,'password:',pexpect.EOF])
        if i==0:
            p.sendline('yes')

            i=p.expect([ssh_newkey,'password:',pexpect.EOF])
        if i==1:
            p.sendline(self.switchPassword)
        p.sendline('enable')
        p.expect('Password:')
        p.sendline(self.switchPassword)
        p.expect('LinuxS5000#')
        p.sendline('configure')
        p.expect('LinuxS5000\(conf\)\#')
        p.sendline('fc zone %s'%(zoneName))
        p.sendline('\n')
        p.expect('LinuxS5000\(conf\-fc\-zone\-%s\)\#'%(zoneName))
        p.sendline('member %s'%(wwpnSwitch0) )
        p.sendline('\n')
        p.expect('LinuxS5000\(conf\-fc\-zone\-%s\)\#'%(zoneName))
        
        p.sendline('member %s'%(wwpnSwitch1) )
        p.sendline('\n')
        p.expect('LinuxS5000\(conf\-fc\-zone\-%s\)\#'%(zoneName))
        
        p.sendline('member %s'%(wwpnNIC) )
        p.sendline('\n')
        p.expect('LinuxS5000\(conf\-fc\-zone\-%s\)\#'%(zoneName))
        p.sendline('\n')
        p.sendline('do write')
        p.sendline('\n')
        p.expect('LinuxS5000\(conf\-fc\-zone\-%s\)\#'%(zoneName))
        p.sendline('\n')
        p.sendline('exit')
        p.expect('LinuxS5000\(conf\)\#')
        p.sendline('\n')
        p.sendline('fc zoneset %s'%(zoneset))
        p.sendline('\n')
        p.expect('LinuxS5000\(conf\-fc\-zoneset\-%s\)\#'%(zoneset))
        p.sendline('\n')
        p.sendline('member %s'%(zoneName))
        p.sendline('\n')
        p.expect('LinuxS5000\(conf\-fc\-zoneset\-%s\)\#'%(zoneset))
        p.sendline('\n')
        p.sendline('do write')
        p.sendline('\n')
        p.expect('LinuxS5000\(conf\-fc\-zoneset\-%s\)\#'%(zoneset))
        p.sendline('\n')
        p.sendline('exit')
        p.expect('LinuxS5000\(conf\)\#')
        p.sendline('\n')
        p.sendline('fcoe-map default_full_fabric')
        p.sendline('\n')
        p.expect('LinuxS5000\(conf\-fcoe\-default\_full\_fabric\)\#')
        p.sendline('\n')
        p.sendline('fcoe-map default_full_fabric')
        p.sendline('\n')
        p.expect('LinuxS5000\(conf\-fmap\-default\_full\_fabric\-fcfabric\)\#')
            
#p=zoning()
#p.ConfigZone('NIC.Slot.2-2-1')

