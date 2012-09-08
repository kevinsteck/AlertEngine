'''
Created on Aug 28, 2012

@author: kevin
'''
from datetime import datetime
from datetime import timedelta
from collections import OrderedDict

class Group:
    def __init__(self, groupId, alert, escalate, ack, suppress, clear):
        self.__groupId = groupId
        self.__shouldAlert = alert
        self.__shouldEscalate = escalate
        self.__shouldAck = ack
        self.__shouldSuppress = suppress
        self.__shouldClear = clear
        self.__timeProfiles = []
        self.__holidayProfiles = []
        self.__levels = OrderedDict()
        
    def Id(self):
        return self.__groupId
        
    def AddLevel(self, index, users, escalateTime):
        if(self.__levels.has_key(index)):
            #choosing to ignore escalateTime here since it was already set
            self.__levels[index].AddUsers(users)
        else:
            level = Level(escalateTime)
            level.AddUsers(users)
            self.__levels[index] = level
    
    def GetRecipients(self, level):
        recipients = []
        print 'Getting recipients for level: ' + str(level)
        for i in range(level+1):
            key = self.__GetKey(i)
            recipients.extend(self.__levels[key].GetUsers())
        return recipients
    
    def GetSize(self):
        return len(self.__levels)
    
    def GetEscalateTime(self, level):
        key = self.__GetKey(level)
        return self.__levels[key].GetEscalateTime()
        
    def __GetKey(self, level):
        return self.__levels.keys()[level]
    
    def ShouldSend(self, alertType):
        if(alertType == 'alert'):
            return self.__shouldAlert
        if(alertType == 'escalate'):
            return self.__shouldEscalate
        if(alertType == 'ack'):
            return self.__shouldAck
        if(alertType == 'suppress'):
            return self.__shouldEscalate
        if(alertType == 'clear'):
            return self.__shouldClear
        return False
    
class GroupCache:
    __groupList = {}
    
    def __init__(self):
        print 'Building GroupCache'
        self.__BuildGroups()
        
    def __BuildGroups(self):
        #just a test group
        newGroup = Group(1, True, True, True, True, True)
        newGroup.AddLevel(0, 'kevinsteck@gmail.com', 1)
        newGroup.AddLevel(1, 'kevinsteck@gmail.com', 1)
        newGroup.AddLevel(2, 'kevinsteck@gmail.com', 1)
        self.__AddGroup(newGroup)
        #another test group
        newGroup1 = Group(2, True, True, True, True, True)
        newGroup1.AddLevel(0, 'kevinsteck@gmail.com', 2)
        newGroup1.AddLevel(1, 'kevinsteck@gmail.com', 2)
        newGroup1.AddLevel(2, 'kevinsteck@gmail.com', 2)
        self.__AddGroup(newGroup1)
        #another test
        newGroup1 = Group(3, True, True, True, True, True)
        newGroup1.AddLevel(0, 'kevinsteck@gmail.com', 5)
        self.__AddGroup(newGroup1)
    
    def __AddGroup(self, group):
        if(not GroupCache.__groupList.has_key(group.Id())):
            GroupCache.__groupList[group.Id()] = group
            
    def GetGroup(self,groupId):
        print 'Getting groupId: ' + str(groupId)
        if(GroupCache.__groupList.has_key(groupId)):
            return GroupCache.__groupList[groupId]
        else:
            return None
    
class Level:
    #escalateTime in mins
    def __init__(self, escalateTime):
        self.__users = []
        self.__escalateTime = escalateTime

    def AddUsers(self, users):
        self.__users.append(users)
        
    def GetEscalateTime(self):
        return self.__escalateTime
        
    def GetUsers(self):
        return self.__users

#not using this right now but will need to implement for better user types
class User:
    def __init__(self):
        pass
    def SendAlert(self, msg):
        pass
    def Send(self):
        pass
    
class GroupInstance:
    __grpCache = GroupCache()
    
    def __init__(self, groupId):
        self.__groupId = groupId
        self.__lastSentLevel = 0
        self.__currentLevel = 0
        self.__nextAction = datetime.max
        
    def CurrentLevel(self):
        return self.__currentLevel
    
    def NextActionTime(self):
        return self.__nextAction
    
    def __GetLastLevelRecipients(self, group):
        return group.GetRecipients(self.__lastSentLevel)
            
    def __GetCurrentLevelRecipients(self, group):
        return group.GetRecipients(self.__currentLevel)
    
    def __ShiftLevelForward(self, group):
        print "Shift Group Size: " + str(group.GetSize()) + " Current level: " + str(self.__currentLevel)
        if(group.GetSize() > self.__currentLevel + 1):
            self.__nextAction = datetime.utcnow() + timedelta(minutes = group.GetEscalateTime(self.__currentLevel))
            self.__currentLevel = self.__currentLevel + 1
        else:
            print 'Reached Max Level'
            self.__nextAction = datetime.max
            
    def __RecalculateCurrentLevel(self, group):
        if(group.GetSize() > self.__lastSentLevel + 1):
            self.__nextAction = datetime.utcnow() + timedelta(minutes = group.GetEscalateTime(self.__lastSentLevel))
        else:
            print 'Reached Max Level... again!'
            self.__nextAction = datetime.max
    
    def __SetNoAction(self):
        self.__nextAction = datetime.max
        
    def GetSuppressionRecipients(self):
        recipients = []
        group = GroupInstance.__grpCache.GetGroup(self.__groupId)
        if(group is not None):
            recipients.extend(self.__GetLastLevelRecipients(group))
            self.__RecalculateCurrentLevel(group)
        print 'Next action time: ' + str(self.__nextAction)
        return recipients
            
    def GetRecipients(self, alertType):
        recipients = []
        group = GroupInstance.__grpCache.GetGroup(self.__groupId)
        if(group.ShouldSend(alertType)):
            if(group is not None):
                if(alertType == 'alert' or alertType == 'escalate'):
                    recipients.extend(self.__GetCurrentLevelRecipients(group))
                    self.__lastSentLevel = self.__currentLevel
                    self.__ShiftLevelForward(group)
                if(alertType == 'ack' or alertType == 'suppress' or alertType == 'clear'):
#                    recipients.extend(self.__GetPreviousLevelRecipients(group))
                    recipients.extend(self.__GetLastLevelRecipients(group))
                    self.__SetNoAction()
        print 'Next action time: ' + str(self.__nextAction)
        return recipients