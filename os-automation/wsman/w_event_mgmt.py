from w import wsman
from w_job_mgmt import wsman_jobMgmt
import logging

class w_event_mgmt(wsman):
    def __init__(self):
        self.conn=wsman('172.16.64.227')
        #print self.conn.enumerate('dcim_efconfigurationservice')
        
        p= self.conn.enumerate('dcim_eventfilter')
        for i in p.keys():
            print i
w_event_mgmt()