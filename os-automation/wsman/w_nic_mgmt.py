# -*- coding: utf-8 -*-
from w_job_mgmt import wsman_jobMgmt
import logging


class wsman_NICMgmt:
    '''
    network management class
    '''
    def __init__(self, w):
        self.conn = w
        self.job = wsman_jobMgmt(self.conn)

    def getAllNIC(self):
        '''
        Returns all available network ports
        '''
        nics = []
        result = self.conn.enumerate('dcim_nicview')
        if result:
            for nic in result:
                nics.append(result[nic]['FQDD'])
        return nics
                

    def getLinkStatus(self, FQDD):
        '''
        Returns network interface port Connected or disconnected
        :param FQDD: network port FQDD
        '''
        instanceID = '%s:LinkStatus' % FQDD
        p = self.conn.get('dcim_nicenumeration', instanceID)
        return p[instanceID]['CurrentValue']

    def getFCoEOffloadSupport(self, fqdd):
        '''
        Returns network interface port support FcoE offload or not
        :param fqdd: network interface port FQDD
        '''

        instanceID = '%s:FCoEOffloadSupport' % (fqdd)
        p = self.conn.get('dcim_nicstring', instanceID)
        return p[instanceID]['CurrentValue']

    def getiSCSIOffloadSupport(self, fqdd):
        '''
        Returns network interface port support  iSCSI offload or not
        :param fqdd: network interface port FQDD
        '''
        instanceID = '%s:iSCSIOffloadSupportt' % (fqdd)
        p = self.conn.get('dcim_nicstring', instanceID)
        return p[instanceID]['CurrentValue']

    def getiSCSIBootSupport(self, fqdd):
        '''
        Returns network interface port support iSCSI boot support or not
        :param fqdd: network interface port FQDD
        '''
        instanceID = '%s:iSCSIBootSupport' % (fqdd)
        result = self.conn.get('dcim_nicstring', instanceID)
        if result:
            return result[instanceID]['CurrentValue']
        else:
            return False

    def getPXEBootSupport(self, fqdd):
        '''
        Returns network interface port support PXE boot support or not
        :param fqdd: network interface port FQDD
        '''
        instanceID = '%s:PXEBootSupport' % (fqdd)
        result = self.conn.get('dcim_nicstring', instanceID)
        if result:
            return result[instanceID]['CurrentValue']
        else:
            return False

    def getFCoEBootSupport(self, fqdd):
        '''
        Returns network interface port support FCoE boot or not
        :param fqdd: network interface port FQDD
        '''
        instanceID = '%s:FCoEBootSupport' % (fqdd)
        result = self.conn.get('dcim_nicstring', instanceID)
        if result:
            return result[instanceID]['CurrentValue']
        else:
            return False

    def getNicPartitioningSupport(self, fqdd):
        '''
        Returns network interface port support nit partitioning or not
        :param fqdd: network interface port FQDD
        '''
        instanceID = '%s:NicPartitioningSupport' % (fqdd)
        p = self.conn.get('dcim_nicstring', instanceID)
        return p[instanceID]['CurrentValue']

    def getNicPartitioningEnabled(self, fqdd):
        '''
        Returns network interface port nit partition enabled or not
        :param fqdd: network interface port FQDD
        '''
        instanceID = '%s:NicPartitioning' % (fqdd)
        p = self.conn.get('dcim_nicenumeration', instanceID)
        return p[instanceID]['CurrentValue']

    def getVirtualizationMode(self, fqdd):
        '''
        Returns network interface port virtualization mode
        :param fqdd: network interface port FQDD
        '''
        instanceID = '%s:VirtualizationMode' % (fqdd)
        p = self.conn.get('dcim_nicstring', instanceID)
        return p[instanceID]['CurrentValue']

    def getCurrentMACAddress(self, fqdd):
        '''
        Returns network interface port MAC address
        :param fqdd: network interface port FQDD
        '''
        instanceID = '%s:MacAddr' % (fqdd)
        p = self.conn.get('dcim_nicstring', instanceID)
        return p[instanceID]['CurrentValue']

    def monitorJob(self, jobID):
        '''
        this function monitor LC job and returns True if successfuly completed
        :param jobID:
        '''
        if jobID:
            logging.debug("job id :" + jobID)
            return self.job.monitorJob(jobID)
        else:
            logging.error("Error: Config Job Not Created")
            return False

    def getLegacyBootProto(self, fqdd):
        '''
        Returns Legacey boot proto used
        :param fqdd: network interface port FQDD
        '''
        instanceID = '%s:%s' % (fqdd, 'LegacyBootProto')
        p = self.conn.get('dcim_nicenumeration', instanceID)
        if p :
            return p[instanceID]['CurrentValue']
        else:
            logging.error("get Failed:")
            logging.debug(p)

    def SetAttribute(self, fqdd, name, value):
        '''
        Returns True if successfuly set NIC setting for given attribute name
        and value
        :param fqdd: network interface port FQDD
        :param name:
        :param value:
        '''
        logging.debug("Setting %s:%s" % (name, value))
        result = self.conn.invoke('dcim_nicservice',
                                  'setattribute', {
                                        'Target': '%s' % (fqdd),
                                        'AttributeName': '%s' % name,
                                        'AttributeValue': '%s' % value
                                        })
        if result:
            if result['SetAttribute_OUTPUT']['ReturnValue'] == '0':
                return True
        return False

    def SetAttributes(self, fqdd, names, values):
        '''
        set attributes
        :param fqdd:
        :param names:
        :param values:
        '''
        result = self.conn.invoke('dcim_nicservice', 'setattributes', {
                                    'Target': '%s' % (fqdd),
                                    'AttributeName': names,
                                    'AttributeValue': values
                                    })
        logging.debug(result)
        if result['SetAttributes_OUTPUT']['ReturnValue'] == '0':
            return True
        else:
            return False

    def CreateTargetedConfigJob(self, fqdd, delay=None):
        if delay:
            result = self.conn.invoke('dcim_nicservice',
                                      'createtargetedconfigjob', {
                                            'Target': '%s' % fqdd,
                                            'RebootJobType': '1',
                                            'ScheduledStartTime': 'TIME_NOW'
                                            })
        else:
            result = self.conn.invoke('dcim_nicservice',
                                      'createtargetedconfigjob', {
                                            'Target': '%s' % fqdd,
                                            'RebootJobType': '1'
                                            })
        if result['CreateTargetedConfigJob_OUTPUT']['ReturnValue'] == '4096':
            return result['CreateTargetedConfigJob_OUTPUT']['Selector: InstanceID']
        else:
            return False

    def creatAndmonitorJob(self, fqdd, delay='TIME_NOW'):
        jobID = self.CreateTargetedConfigJob(fqdd, delay)
        if jobID:
            logging.info("Config Job created successfully ID:%s" % (jobID))
            return self.job.monitorJob(jobID)
        else:
            logging.error("Error: Config Job Not Created")
            return False

    def DeletePendingConfiguration(self, fqdd):
        result = self.conn.invoke('dcim_nicservice',
                                  'deletependingconfiguration', {
                                        'Target': 'BIOS.Setup.1-1'
                                        })
        if result:
            return True
        else:
            return False
        
    def biosdevName(self):
        names = []

        nics = self.getAllNIC()

        for nic in nics:
            # print nic
            if 'Integrated' in nic or 'Embedded' in nic:
                name = 'em'
            else:
                name = 'p'
            n = nic.split('.')[2].split('-')
            if 'Integrated' in nic:
                name += '%s' % (n[1])
            elif 'Embedded' in nic:
                
                name += '%s' % (n[0])
            else:
                name += '%sp%s' % (n[0], n[1])
            
            # if n[2]=='1':
            #    if self.getNicPartitioningSupport(nic)=='Available':
            #        if self.getNicPartitioningEnabled(nic) != 'Disabled':
            #            name+='_%s'%(n[2])
                        
            if n[2] > '1':
                    name += '_%s' % (n[2])
            names.append(name)
        
            
        return names
    def getWWPN(self, fqdd):
        instanceID = '%s:WWPN' % (fqdd)
        result = self.conn.get('dcim_nicstring', instanceID)
        return result[instanceID]['CurrentValue']

