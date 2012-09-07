'''
Created on Aug 19, 2012

@author: kevin
'''
from collections import deque
from datetime import datetime
from SimpleXMLRPCServer import SimpleXMLRPCServer
from AlertEngine.ProcessItems import AlertItem, AckItem, SuppressItem, ClearItem
from AlertEngine.AlertGroup import GroupInstance
from AlertEngine.Client import ClientTest 
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
    
    def Suppress(self, appId, uniqueId):
        suppress = SuppressItem(uniqueId)
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
#        for a in AlertCore.__alertList.values():
#            print a.NextActionTime()
        actionable = filter(lambda x: x.NextActionTime() < currentTime, AlertCore.__alertList.values())
        for a in actionable:
            a.SendAlert()
        AlertCore.UpdateActionTime()
    
    @staticmethod
    def UpdateActionTime():
        nextTime = datetime.max
        for a in AlertCore.__alertList.values():
            if(a.NextActionTime() < nextTime):
                nextTime = a.NextActionTime()
            
class AlertCoreWorker(threading.Thread):
    def __init__(self, alertCore):
        self.__Core = alertCore
        threading.Thread.__init__(self)
    def run(self):
        while True:
            print 'Processing Action Queue'
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
            print 'Doing work'
            self.__alertCore.ProcessAlertState()
            time.sleep(5)
            
class AlertInstance:
    def __init__(self, uniqueId, message, groupList, ttl):
        self.__uniqueId = uniqueId
        self.__message = message
        self.__groupInstanceList = []
        self.__ttl = ttl
        self.__state = 'alert'
        self.__nextAction = datetime.max
        for g in groupList:
            self.__groupInstanceList.append(GroupInstance(g))
        self.__Send('alert')
        #self.SetupSmtp(username, userPass, fromAddr, smtpServer, smtpPort)
        
    def __Send(self, alertType):
        if(not (self.__state == 'ack' or self.__state == 'suppress')):
            for g in self.__groupInstanceList:
                recipients = g.GetRecipients(alertType)
                print 'Would have sent to: ' + str(recipients)
                #self.__SendMail(recipients, 'fill this in')
                self.UpdateNextActionTime()
                print 'Next action time: ' + str(self.__nextAction)
        
    def UpdateNextActionTime(self):
        closestTime = datetime.max
        for g in self.__groupInstanceList:
            if(g.NextActionTime() < closestTime):
                closestTime = g.NextActionTime()
        self.__nextAction = closestTime
        
    def NextActionTime(self):
        return self.__nextAction
                
    def SendAlert(self):
        self.__Send('alert')
        
    def Ack(self):
        self.__Send('ack')
        self.__state = 'ack'
    
    def Suppress(self):
        self.__Send('suppress')
        self.__state = 'suppress'
    
    def Clear(self):
        self.__Send('clear')
            
    def __SetupSmtp(self, username, userPass, fromAddr, smtpServer, smtpPort):
        self.__username = username
        self.__password = userPass
        self.__fromAddr = fromAddr
        self.__smtp = smtplib.SMTP(smtpServer, smtpPort)

    def __SendMail(self, toAddr, msg):
        self.smtp.ehlo()
        self.smtp.starttls()
        self.smtp.ehlo()
        self.smtp.login(self.__username, self.__password)
        self.smtp.sendmail(self.__fromAddr, toAddr, msg)
        self.smtp.quit()     
            

            
alertcoreThreader = AlertCoreThreader()
alertcoreThreader.start()
clientTest = ClientTest()
clientTest.start()