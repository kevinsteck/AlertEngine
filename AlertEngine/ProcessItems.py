'''
Created on Aug 28, 2012

@author: kevin
'''
from AlertEngine.AlertCore import AlertInstance

class Processable:
    def Process(self, alertList):
        raise NotImplementedError, "Ut Oh! Don't use this directly!"
    
class AlertItem(Processable):
    def __init__(self,uniqueId, message, groupList, ttl):
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