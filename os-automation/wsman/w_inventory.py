from w import wsman
from w_job_mgmt import *
import logging

import re

class wsman_inventory:
    def __init__(self,w):
        self.conn=w
    def get_inventory(self):
        inv=self.conn.enumerate('dcim_softwareidentity')
        ret=dict()
        if inv:
            for i in inv:
                ret[inv[i]['InstanceID']]= inv[i]['VersionString']
        return ret
    def installFromURI(self):
        self.conn.invoke('dcim_softwareinstallationservice', 'installfromuri',{'URI':'http://100.98.4.4/test/1.EXE','Target':'DCIM:INSTALLED#301_C_RAID.Integrated.1-1'})
          
    
        