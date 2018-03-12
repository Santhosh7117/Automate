#!/usr/bin/python
import sys
from command import Command
from w import wsman
from w_lc_mgmt import wsman_LCMgmt
import os
import logging

logging.basicConfig(level=logging.DEBUG)
w=wsman('100.98.4.76')
lc=wsman_LCMgmt(w)

listdir=os.listdir('test')
print listdir


#fName='R630_UEFI_RAID0.xml'
for file in listdir:
	fName=file
	jobid=lc.ImportSystemConfiguration(IPAddress='100.98.4.4',ShareName='public/test',ShareType='2',FileName=fName)
	lc.monitorJob(jobid)

	argStr=file.replace('.xml','')
	print argStr.split('_')
	kopt="ignore_loglevel "
	if 'ISCSI' in file:
		kopt +="rd.iscsi.ibft=1"
	family="RedHatEnterpriseLinux6"
	distro="Red Hat Enterprise Linux 6.9" 
	machine="%s-%s"%(argStr.split('_')[0],argStr.split('_')[1])
	whiteboard=argStr

	tasks="--task /distribution/beaker/Sanity/reboot-tests --taskparam=REBOOT_COUNT=10 \
	--task /CoreOS/beaker/Sanity/var-log-analysis \
	--task /installation/beaker/Install/check-installation \
	--taskparam=INSTALL_MODE_CHECK_VALUE=%s"%(argStr.split('_')[3])

   	cmdline='bkr workflow-simple --kernel-options=\"%s\"\
   					--family=%s --distro=\"%s\"\
   					--arch=x86_64 \
   					--variant=Server\
   					--task /distribution/install \
    				--machine=%s \
    				--method=http \
    				--whiteboard=%s %s'%(kopt,family,distro,machine,whiteboard,tasks)
	cmd=Command(cmdline)
	cmd.run()
	jobID = cmd.output[0].split('[')[1].replace('\'', '').replace(']', '')
	print jobID
	os.system('bkr job-watch %s' % (jobID))
    				
