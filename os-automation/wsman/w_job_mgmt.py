# -*- coding: utf-8 -*-
from w import wsman
import time
import sys
import logging
class wsman_jobMgmt:
    def __init__(self,w):
        self.conn=w
        
    def getJobStatus(self,instanceID):
        logging.debug('inside getJobStatus')
        return self.conn.get('dcim_lifecyclejob', instanceID)
        
    def monitorJob(self,jobID):

        status0 =self.getJobStatus(jobID)
        if not status0:
            return False
        status=status0[jobID]['JobStatus']
        oldstatus=""
        while 'Completed' not in status  and 'Failed' not in status :
            
            status0 =self.getJobStatus(jobID)
            if status0 :
                status=status0[jobID]['JobStatus']
            else:
                return  status0
                logging.error("failed to get status for job:%s"%(jobID))
            if status == oldstatus:
                sys.stdout.write('.')
            else:
                return "\n"
                sys.stdout.write(status)
                oldstatus=status
            time.sleep(2)
        time.sleep(30)
        return True
    def LC(self):
        #r=self.conn.enumerate('dcim_lifecyclejob')
        r=self.conn.enumerate('dcim_jobservice')
        #for i in r:
        #    print i
    def SetupJobQueue(self,jobList):
        jl=','.join(jobList)
        self.conn.invoke('dcim_jobservice','setupjobqueue',{'JobArray':'%s'%(jl),'StartTimeInterval':'TIME_NOW'})
    def CreateJob(self,jobType=None,JobParameterNames=None,JobParameterValues=None):
        '''
        

        :param JobType: ConfigRAID:RAID.Integrated.1-1,ConfigBIOS: BIOS.Setup.1-1,ConfigNIC:< NIC FQDD>
        :param JobParameterNames:
        :param JobParameterValues:
        '''
        arg=dict()
        if jobType:
            arg['JobType']='%s'%(jobType)
        if JobParameterNames:
            arg['JobParameterNames']='%s'%(JobParameterNames)
            arg['JobParameterValues']='%s'%(JobParameterValues)
        
        self.conn.invoke('dcim_jobservice','createjob',arg)
    def DeleteJobQueue(self,JobID="JID_CLEARALL"):
        
        arg={'JobID':JobID}
        self.conn.invoke('dcim_jobservice','deletejobqueue',arg)
        
#con=wsman('172.16.64.213')
#j=wsman_jobMgmt(con)
#j.LC()
    

