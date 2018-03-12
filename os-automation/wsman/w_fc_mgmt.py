from w import wsman
from w_job_mgmt import wsman_jobMgmt
import logging

class w_fc_mgmt(wsman):
    def __init__(self,w):
        self.conn=w
    def getWWPN(self):
       print  self.conn.enumerate('dcim_fcview')
        