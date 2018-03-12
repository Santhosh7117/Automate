#***************************************************************************
# Test Case Name   : testSchedule
# Description    : General library to install os on SUTs
# Author         : Shilpa
# Created        : 2015-02-27
#***************************************************************************

#*************************General python Imports****************************
import os
# import sys
import time
# import subprocess
# import re
import logging
#******************************Local Imports********************************
from testconfig import testconfig
from execTest import execTest
from multiprocessing import Process
#*******************************Main Script*********************************
class testSchedule:
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.configFile = "sys.xml"
        if os.path.isfile(self.configFile) :
            
            self.conf = testconfig(self.configFile)
            self.runTests()
        else:
            logging.debug('Server configuration file not found')
        
    def runTests(self):
        self.systems = self.conf.getSystems()
        jobs = []
        for system in self.systems: 
            install_tests = self.conf.getTestCases1(system)
            tests = self.conf.getTestCases2(system, install_tests[0])
            p = Process(target=execTest, args=(install_tests, tests, self.conf, system))
            jobs.append(p)
            p.start()

p = testSchedule()

