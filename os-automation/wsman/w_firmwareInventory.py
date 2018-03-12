#-*- coding: utf-8 -*-
from w import wsman
from w_job_mgmt import wsman_jobMgmt
import logging
import sys


class wsman_FirmwareInventory:
    '''
    network management class
    '''
    def __init__(self, w):
        self.conn = w
        self.job = wsman_jobMgmt(self.conn)

    def getFirmwareInventory(self):
        '''
        Returns all available network ports
        '''
        result = self.conn.enumerate('dcim_softwareidentity')
        #result = self.conn.enumerate('dcim_softwareinstallationservice')
        if result:
            return result
    def GetSoftwareIdentity(self):
        result = self.conn.inv
                
    def compare_firmware(IDRAC_INFO, root_uri, catalog_file, model):
	fw = []
	fw_list = {'ret':True, 'Firmwares':[]}

	response = send_get_request(IDRAC_INFO, root_uri + '/redfish/v1/UpdateService/FirmwareInventory/')



        for i in data['Members']:
            if 'Installed' in i['@odata.id']:
                fw.append(i['@odata.id'])

        # read catalog file
        tree = ET.parse(catalog_file)
        root = tree.getroot()
        for inv in fw:
            ver = inv.split('-')[1]
            version = '0'
            path = ""
            for i in root.findall('.//Category/..'):
                        for m in i.findall('.//SupportedDevices/Device'):
                            if m.attrib['componentID'] == ver:
                                for nx in i.findall('.//SupportedSystems/Brand/Model/Display'):
                                    if nx.text == model:
                                        if LooseVersion(i.attrib['vendorVersion']) > LooseVersion(version):
                                            version = i.attrib['vendorVersion']
                                            path = i.attrib['path']

            if path != "":
                fw_list['Firmwares'].append({ 'curr':'%s' % os.path.basename(inv).replace('Installed-%s-'%ver,''), 'latest':'%s' % version, 'path':'%s' % path })
	else:
	    fw_list['ret'] = False
	return fw_list




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


    def SetAttribute(self, uri, fwInstanceID):
        '''
        Returns True if successfuly set NIC setting for given attribute name
        and value
        :param fqdd: network interface port FQDD
        :param name:
        :param value:
        '''
        result = self.conn.invoke('dcim_softwareinstallationservice',
                                  'installfromuri', {
                                        'URI': uri,
                                        'Target': "%s" % fwInstanceID,
                                        })
        print result
        if result:
            if result['SetAttribute_OUTPUT']['ReturnValue'] == '0':
                return True
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



w=wsman(sys.argv[1])
net=wsman_FirmwareInventory(w)
fw= net.getFirmwareInventory()
print fw
for i in  fw:
    print fw[i]
    #print "%s:%s"%(fw[i]['VersionString'],fw[i]['InstanceID'])

net.SetAttribute( ['http://100.98.4.4/test/FW/BIOS.EXE'],'DCIM:INSTALLED#741__BIOS.Setup.1-1')


#print net.getAllNIC()
