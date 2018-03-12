import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#sys.path.append( '/root/auto/R720/' )

from DellWsman import iDRAC
import re
import logging
import time

class wsman:
    def __init__(self, host, user='root', password='calvin'):
        self.conn = iDRAC(host, user, password)

    def __parseData(self, data):
        '''
        :param data:
        '''
        enumDataA = dict()
        enumDataC = dict()
        startcls = False
        for line in data.split('\n'):
            if re.match("^DCIM_", line, re.M | re.I):

                cls = line.strip()
                if enumDataA:
                    enumDataC[enumDataA['InstanceID']] = enumDataA
                    enumDataA = {}
                startcls = True
                continue
            if startcls and line.strip() != "":
                tmp = line.split("=")
                if len(tmp) > 1:
                    enumDataA[tmp[0].strip()] = tmp[1].strip()
                else:
                    enumDataA[tmp[0].strip()] = None
        if not 'InstanceID' in enumDataC and 'InstanceID' in enumDataA:
            enumDataC[enumDataA['InstanceID']] = enumDataA
        return enumDataC
    def __parseResult(self, result):
        '''
        :param result:
        '''
        A = dict()
        startRE = False
        for line in result.split('\n'):
            if re.match("\w+OUTPUT$", line, re.M | re.I):
                RE = line.strip()
                A[RE] = {}
                startRE = True
            if startRE and line.strip() != "" and '=' in line:
                tmp = line.split('=')
                A[RE][tmp[0].strip()] = tmp[1].strip()
        return A
    def enumerate(self, className):
        logging.debug('Inside Enumerate')
        enum = getattr(getattr(self.conn, className), 'enumerate')()
        
        logging.debug(enum.prettyresponse)
        if not enum.hasfault:
            logging.info('Enumerate successful with class:%s' % (className))
            return self.__parseData(enum.prettyresponse)
        else:
            logging.error('enumerate class :%s Failed' % (className))
            logging.error(enum.xmlresponse)
            return not enum.hasfault
        
        
        
    def get(self, className, instanceID):
        logging.debug('Inside get')
        epr = getattr(self.conn, className).createSelectorSetXML(InstanceID=instanceID)
        result = getattr(getattr(self.conn, className), 'get')(epr)
        logging.debug(result.prettyresponse)
        if not result.hasfault:
            logging.debug('get successful with class:%s and instanceID:%s' % (className, instanceID))
            return self.__parseData(result.prettyresponse)
        else:
            logging.error('Get instanceID:%s Failed' % (instanceID))
            logging.error(result.xmlresponse)
            return False

    def set(self, className, instanceID, property, value):
        logging.debug('inside set')
        epr = getattr(self.conn, className).createSelectorSetXML(InstanceID=instanceID)
        result = getattr(getattr(self.conn, className), 'set')(epr, property, value)
        # print result.prettyresponse
        return self.__parseData(result.prettyresponse)
    
    def invoke(self, className, method, args):
        logging.debug('inside invoke')
        result = getattr(getattr(self.conn, className), method)(**args)
        #print result.prettyresponse
        
        logging.debug(result.prettyresponse)
        if not result.hasfault:
            logging.debug('invoke class:%s method:%s args:%s' % (className, method, args))
            return self.__parseResult(result.prettyresponse)
            
        else:
            logging.error('invoke Failed forclass:%s method:%s args:%s' % (className, method, args))
            fault=self.__parseResult(result.prettyresponse)
            if fault['%s_OUTPUT'%method]['MessageID'] == 'LC062':
                
                logging.info('sleep 60sec to wait Export or import server profile operation ')
                time.sleep(60)
                logging.debug('invoke  again')
                result = getattr(getattr(self.conn, className), method)(**args)
                if not result.hasfault:
                    logging.debug('invoke class:%s method:%s args:%s' % (className, method, args))
                    return self.__parseResult(result.prettyresponse)
            return result.hasfault
        
