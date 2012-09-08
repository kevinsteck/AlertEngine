'''
Created on Aug 19, 2012

@author: kevin
'''

import time
import xmlrpclib
import threading
from datetime import datetime
from datetime import timedelta

class ClientTest(threading.Thread):
    def __init__(self):
        print 'Starting client...'
        self.__client = xmlrpclib.ServerProxy('http://localhost:9000')
        threading.Thread.__init__(self)
    def run(self):
        self.__currentCount = 0
        while(True):
            self.__client.Alert(self.__currentCount, 'test', [1], 10)
            time.sleep(5)
            self.__client.Suppress(self.__currentCount, datetime.utcnow() + timedelta(minutes = 1))
#            self.__client.Alert(self.__currentCount+1, 'testing', [2], 10)
#            self.__client.Alert(self.__currentCount+2, 'testing others', [1, 2], 10)
#            self.__client.Alert(self.__currentCount+3, 'testing others', [3], 10)
#            time.sleep(140)
#            self.__client.Ack(self.__currentCount)
            time.sleep(400)
            
