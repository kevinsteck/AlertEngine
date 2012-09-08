'''
Created on Aug 19, 2012

@author: kevin
'''
from collections import deque
from datetime import datetime
from SimpleXMLRPCServer import SimpleXMLRPCServer
from AlertEngine.Client import ClientTest
from AlertEngine.ProcessItems import AlertItem, AckItem, SuppressItem, ClearItem
import threading
import time
import smtplib

class AlertCore(threading.Thread):
    NextAction = datetime.max
    __alertList = {}
    __eventQueue = deque()
    
    def __init__(self):
        self.__SetupServer()
        threading.Thread.__init__(self)
    
    def run(self):
        print 'Starting server'
        self.__StartServer()
    
    def __SetupServer(self):
        self.__server = SimpleXMLRPCServer(('localhost', 9000), allow_none = True)
        self.__server.register_function(self.Alert)
        self.__server.register_function(self.Clear)
        self.__server.register_function(self.Ack)
        self.__server.register_function(self.Suppress)
        
    def __StartServer(self):
        try:
            self.__server.serve_forever()
        except:
            print 'something went wrong with the server'
    
    def Alert(self, uniqueId, message, groupList, ttl):
        alert = AlertItem(uniqueId, message, groupList, ttl)
        AlertCore.__eventQueue.append(alert)
        
    def Ack(self, uniqueId):
        ack = AckItem(uniqueId)
        AlertCore.__eventQueue.append(ack)
    
    def Suppress(self, uniqueId, suppressTime):
        print 'Suppressed until: ' + str(suppressTime)
        suppress = SuppressItem(uniqueId, suppressTime)
        AlertCore.__eventQueue.append(suppress)
        
    def Clear(self, uniqueId):
        clear = ClearItem(uniqueId)
        AlertCore.__eventQueue.append(clear)
    
    @staticmethod
    def ProcessQueue():
        while AlertCore.__eventQueue:
            item = AlertCore.__eventQueue.popleft()
            item.Process(AlertCore.__alertList)
    
    @staticmethod
    def ProcessAlertState():
        currentTime = datetime.utcnow()
        actionable = filter(lambda x: x.NextActionTime() < currentTime, AlertCore.__alertList.values())
        for a in actionable:
            a.SendNextEvent()
        AlertCore.UpdateActionTime()
    
    @staticmethod
    def UpdateActionTime():
        NextTime = datetime.max
        for a in AlertCore.__alertList.values():
            if(a.NextActionTime() < NextTime):
                NextTime = a.NextActionTime()
            
class AlertCoreWorker(threading.Thread):
    def __init__(self, alertCore):
        self.__Core = alertCore
        threading.Thread.__init__(self)
    def run(self):
        while True:
            self.__Core.ProcessQueue()
            time.sleep(5)

class AlertCoreThreader(threading.Thread):
    def __init__(self):
        self.__alertCore = AlertCore()
        self.__alertCoreWorker = AlertCoreWorker(self.__alertCore)
        threading.Thread.__init__(self)
        
    def run(self):
        self.__alertCore.start()
        self.__alertCoreWorker.start()
        while(True):
            self.__alertCore.ProcessAlertState()
            time.sleep(5)

alertcoreThreader = AlertCoreThreader()
alertcoreThreader.start()
clientTest = ClientTest()
clientTest.start()