# -*- coding: utf-8 -*-
from w import wsman
from w_job_mgmt import wsman_jobMgmt
import logging
import re
from w import wsman
from command import Command
class labInfo():
    def __init__(self):
        self.ip=None
        self.HTML="""<!DOCTYPE html>
<html>
<head>
<style>
table {
    font-family: arial, sans-serif;
    border-collapse: collapse;
    width: 100%;
}

td, th {
    border: 1px solid #dddddd;
    text-align: left;
    padding: 8px;
}

tr:nth-child(even) {
    background-color: #dddddd;
}
</style>
</head>
<body>
<table>
 <tr >
    <th rowspan="2"> IP</th>
    <th rowspan="2"> System Model</th>
    <th rowspan="2"> Service Tag</th>
    <th rowspan="2">Integrated PERC</th>
    <th rowspan="2"> Integrated NIC</th>
    <th rowspan="2">Slot1</th>
    <th rowspan="2">Slot2</th>
    <th rowspan="2">Slot3</th>
    <th rowspan="2">Slot4</th>
    <th rowspan="2">Slot5</th>
    <th rowspan="2">Slot6</th>
    <th rowspan="2">Slot7</th>
    <th rowspan="2">Slot8</th>
    <th colspan="3">CPU Info</th>
    
  </tr>
<tr>
    <th>Model</th>
    <th>Sockets</th>
    <th>Cores per Socket</th>
  </tr>
</tr>
"""
    def getSysInfo(self,ip):
        self.ip=ip
        intNIC=None
        intPERC=None
        self.conn = wsman(self.ip)
        slots={'1':None,'2':None,'3':None,'4':None,'5':None,'6':None,'7':None,'8':None}
        socketCount=0
        out=self.conn.enumerate('dcim_biosstring')
        tag=out['BIOS.Setup.1-1:SystemServiceTag']['CurrentValue']
        model=out['BIOS.Setup.1-1:SystemModelName']['CurrentValue']
        cpu=out['BIOS.Setup.1-1:Proc1Brand']['CurrentValue']
        if out.has_key('BIOS.Setup.1-1:Proc1Brand'):
            socketCount=socketCount+1
        if out.has_key('BIOS.Setup.1-1:Proc2Brand'):
            socketCount=socketCount+1
        if out.has_key('BIOS.Setup.1-1:Proc3Brand'):
            socketCount=socketCount+1
        if out.has_key('BIOS.Setup.1-1:Proc4Brand'):
            socketCount=socketCount+1

        out1=self.conn.enumerate('dcim_biosinteger')
        cores=out1['BIOS.Setup.1-1:Proc1NumCores'] ['CurrentValue']
        
        out2=self.conn.enumerate('dcim_biosenumeration')
        mode=out2['BIOS.Setup.1-1:BootMode']['CurrentValue'] 
        
        out3=self.conn.enumerate('dcim_controllerview')
        for i in out3:
            if 'Integrated' in i:
                intPERC=out3[i]['ProductName']
            if 'RAID.Slot' in i:
                slot_num=i.split('.')[2].split('-')[0]
                slots[slot_num]=out3[i]['ProductName']

        out4=self.conn.enumerate('dcim_nicview')
        for i in out4:
            if 'Integrated' in i:
                intNIC=out4[i]['ProductName']
            if 'Embedded' in i:
                intNIC=out4[i]['ProductName']
                intNIC="(Embedded)"+intNIC

            if 'Slot' in i:
                slot_num=i.split('.')[2].split('-')[0]
                slots[slot_num]=out4[i]['ProductName']
        cpuCount=1
        H="<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"%(self.ip,model,tag,intPERC,intNIC,slots['1'],slots['2'],slots['3'],slots['4'],slots['5'],slots['6'],slots['7'],slots['8'],cpu,socketCount,cores)
        self.HTML=self.HTML+H
    def writeHTML(self):
        self.HTML=self.HTML+"</table></body> </html>"
        fd=open("sysinfo.html","w+")
        fd.write(self.HTML)


         
#cmd=Command('nmap 100.98.4.1/22 -oG - | awk \'/Up$/{print $2}\'')
#cmd.run()
#for i in cmd.output:
#    print i
j=['100.98.4.77','100.98.4.63','100.98.4.18']
a=labInfo()
for i in j:
    a.getSysInfo(i)
a.writeHTML()

