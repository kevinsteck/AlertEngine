'''
Created on Sept 5, 2012

@author: kevin
'''

import time
from datetime import datetime

class TimeProfile:
    def __init__(self, dayOfWeek, startMinutes, endMinutes):
        self.DayOfWeek = dayOfWeek
        self.StartMinutes = startMinutes
        self.EndMinutes = endMinutes
        pass
    
class TimeProfiles:
    pass

class Holiday:
    def __init__(self, start, end, offset):
        self.Start = start
        self.End = end
        #todo: account for offset
        self.Offset = offset

class HolidayProfile:
    def __init__(self, groupId):
        #assuming the profile ranges are associated with a particular group
        # may want to make it a bit more generic
        self.__groupId = groupId
        self.__holidayRanges = []
    
    def __Load(self):
        #database stuff can happen here
        pass
    
    def IsDateTimeActive(self, dateInQuestion):
        active = True
        
        for r in self.__holidayRanges:
            startTime = r.Start
            endTime = r.End
            
            if((startTime <= dateInQuestion) and (dateInQuestion < endTime)):
                active = False
                break
        
        return active
    
    def GetNextActiveTime(self, dateInQuestion):
        foundTime = datetime.min
        
        for r in self.__holidayRanges:
            startTime = r.Start
            endTime = r.End
            
            if((startTime <= dateInQuestion) and (dateInQuestion < endTime)):
                foundTime = endTime if (foundTime < startTime) else foundTime
        
        return foundTime

#for use later
offset = time.timezone if (time.daylight == 0) else time.altzone
gmtOffset = offset / -(60*60)
print gmtOffset