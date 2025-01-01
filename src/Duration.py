class DurationModel:
    def __init__(self, days: int = 0, hours:int = 0, minutes: int = 0, seconds: int = 0):
        self.days = days
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds
    
    def SetHours(self, hours):
        self.hours = hours

    def SetDays(self, days):
        self.days = days

    def SetMinutes(self, minutes):
        self.minutes = minutes

    def SetSeconds(self, seconds):
        self.seconds = seconds
    def __str__(self):
        return f"{self.days} days, {self.hours} hours, {self.minutes} minutes and {self.seconds} seconds"
        
    def ToSecond(self):
        return self.days * 24 * 3600  + self.hours * 3600 + self.minutes * 60 + self.seconds