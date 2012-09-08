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
        self.__suppressTime = datetime.max
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
                print 'Escalate: Would have sent to: ' + str(recipients)
                #self.__SendMail(recipients, 'fill this in')              
            self.UpdateNextActionTime()
        if(alertType == 'ack'  or alertType == 'clear'):
            for g in self.__groupInstanceList:
                recipients = g.GetRecipients(alertType)
                print 'Ack/Suppress/Clear: Would have sent to: ' + str(recipients)
                #self.__SendMail(recipients, 'fill this in')
            self.__nextAction = datetime.max
        if(alertType == 'suppress'):
            for g in self.__groupInstanceList:
                recipients = g.GetRecipients(alertType)
                print 'Suppress: Would have sent to: ' + str(recipients)
            print 'Suppress next time: ' + str(self.__suppressTime)
            self.__nextAction = self.__suppressTime
    
    def __SendSuppressExpire(self):
        for g in self.__groupInstanceList:
            recipients = g.GetSuppressionRecipients()
            print 'Suppression Expired: Would have sent to: ' + str(recipients)
            self.__state = 'escalate'
        self.UpdateNextActionTime()
        
    def UpdateNextActionTime(self):
        closestTime = datetime.max
        for g in self.__groupInstanceList:
            if(g.NextActionTime() < closestTime):
                closestTime = g.NextActionTime()
        self.__nextAction = closestTime
        
    def NextActionTime(self):
        return self.__nextAction
    
    def SendNextEvent(self):
        #current state is suppressed so you can assume this is an expire
        # this may get tricky once i add time profiles
        print 'Sent next event: ' + str(self.__state)
        if(not self.__state == 'suppress'):
            self.__Send(self.__state)
        else:
            self.__SendSuppressExpire()
                
    def SendAlert(self):
        self.__Send('alert')
        self.__state = 'escalate'
        
    def Ack(self):
        self.__Send('ack')
        self.__state = 'ack'
    
    def Suppress(self, suppressTime):
        self.__suppressTime = suppressTime
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
            alert = alertList[self.__uniqueId]
            alert.Ack()
    
class SuppressItem(Processable):
    def __init__(self, uniqueId, suppressTime):
        self.__uniqueId = uniqueId
        self.__suppressTime = suppressTime
    def Process(self, alertList):
        if(alertList.has_key(self.__uniqueId)):
            alert = alertList[self.__uniqueId]
            alert.Suppress(self.__suppressTime)
    
class ClearItem(Processable):
    def __init__(self, uniqueId):
        print uniqueId
        self.__uniqueId = uniqueId
    def Process(self, alertList):
        print self.__uniqueId
        if(alertList.has_key(self.__uniqueId)):
            alert = alertList.pop(self.__uniqueId)
            alert.Clear()