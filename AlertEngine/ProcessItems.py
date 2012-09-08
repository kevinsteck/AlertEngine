'''
Created on Aug 28, 2012

@author: kevin
'''
#from AlertEngine.AlertCore import AlertInstance
from AlertEngine.AlertGroup import GroupInstance 
from datetime import datetime

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
        self.SendAlert()
        #self.SetupSmtp(username, userPass, fromAddr, smtpServer, smtpPort)
        
    def __GetActionableGroups(self):
        groups = []
        for g in self.__groupInstanceList:
            if(g.NextActionTime() < datetime.utcnow()):
                groups.append(g)
        return groups
        
    def __Send(self, alertType):
        if(alertType == 'alert'):
            for g in self.__groupInstanceList:
                recipients = g.GetRecipients(alertType)
                print 'Alert: Would have sent to: ' + str(recipients)
                #self.__SendMail(recipients, 'fill this in')
            self.UpdateNextActionTime()
        if(alertType == 'escalate'):
            groups = self.__GetActionableGroups()
            for g in groups:
                recipients = g.GetRecipients(alertType)
                print 'Esclate: Would have sent to: ' + str(recipients)
                #self.__SendMail(recipients, 'fill this in')              
            self.UpdateNextActionTime()
        if(alertType == 'ack' or alertType == 'suppress' or alertType == 'clear'):
            for g in self.__groupInstanceList:
                recipients = g.GetRecipients(alertType)
                print 'Ack/Suppress/Clear: Would have sent to: ' + str(recipients)
                #self.__SendMail(recipients, 'fill this in')
            self.__nextAction = datetime.max
        
#        print 'Next action time: ' + str(self.__nextAction)
        
    def UpdateNextActionTime(self):
        closestTime = datetime.max
        for g in self.__groupInstanceList:
            if(g.NextActionTime() < closestTime):
                closestTime = g.NextActionTime()
        self.__nextAction = closestTime
        
    def NextActionTime(self):
        return self.__nextAction
    
    def SendEscalate(self):
        self.__Send(self.__state)
                
    def SendAlert(self):
        self.__Send('alert')
        self.__state = 'escalate'
        
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

class Processable:
    def Process(self, alertList):
        raise NotImplementedError, "Ut Oh! Don't use this directly!"
    
class AlertItem(Processable):
    def __init__(self,uniqueId, message, groupList, ttl):
        print 'Created AlertItem'
        self.__uniqueId = uniqueId
        self.__message = message
        self.__groupList = groupList
        self.__ttl = ttl
        
    def Process(self, alertList):
        if(not alertList.has_key(self.__uniqueId)):
            newAlert = AlertInstance(self.__uniqueId, self.__message, self.__groupList, self.__ttl)
            if(self.__ttl > 0):
                alertList[self.__uniqueId] = newAlert
    
class AckItem(Processable):
    def __init__(self,uniqueId):
        self.__uniqueId = uniqueId
    def Process(self, alertList):
        if(alertList.has_key(self.__uniqueId)):
            alert = self.__alertList[self.__uniqueId]
            alert.ack()
    
class SuppressItem(Processable):
    def __init__(self, uniqueId):
        self.__uniqueId = uniqueId
    def Process(self, alertList):
        if(alertList.has_key(self.__uniqueId)):
            alert = alertList[self.__uniqueId]
            alert.suppress()
    
class ClearItem(Processable):
    def __init__(self, uniqueId):
        self.__uniqueId = uniqueId
    def Process(self, alertList):
        if(alertList.has_key(self.__uniqueId)):
            alert = self.__alertList.pop(self.__uniqueId)
            alert.clear()