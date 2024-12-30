class DurationModel:
    def __init__(self, days: int = 0, hours:int = 0, minutes: int = 0):
        self.days = days
        self.hours = hours
        self.minutes = minutes
    
    def SetHours(self, hours):
        self.hours = hours

    def SetDays(self, days):
        self.days = days

    def SetMinutes(self, minutes):
        self.minutes = minutes

    def __str__(self):
        return f"{self.days} days, {self.hours} hours, and {self.minutes} minutes"
        
    def ToMinutes(self):
        return self.days * 24 * 60 + self.hours * 60 + self.minutes