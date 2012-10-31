def plural_if(zstring, zcondition):
    if type(zcondition) is bool:
        plural = zcondition
    else:
        plural = zcondition > 1 or zcondition == 0
        
    return zstring + ("s" if plural else "")

def pretty_timedelta(zdelta):
    if zdelta.days == 0 and zdelta.seconds == 0:
        return "now"
    
    # We will build our string part by part. All strings in this array will be
    # concatenated with a space as delimiter.
    stringParts = []
    
    if zdelta.days < 0:
        ago = True
        days = -zdelta.days % 30
    else:
        ago = False
        days = zdelta.days % 30
        stringParts.append("in")
    
    months = abs(zdelta.days) / 30
    hours = zdelta.seconds / (60 * 60)
    minutes = (zdelta.seconds % (60 * 60)) / 60
    seconds = (zdelta.seconds % 60)
    
    # Add the months part
    if months != 0:
        return "in more than " + str(months) + plural_if(" month", months)
    
    # Add the days part
    if days != 0:
        stringParts += [str(days), plural_if("day", days)]
    
    # Add the hours part
    if hours != 0:
        stringParts += [str(hours), plural_if("hour", hours)]
    
    # Add the minutes part if we're less than 4 hours away
    if minutes != 0 and days == 0 and hours < 4:
        stringParts += [str(minutes), plural_if("minute", minutes)]
        
    # Add the seconds part if we're less than 10 minutes away
    if seconds != 0 and days == 0 and hours == 0 and minutes < 10:
        stringParts += [str(seconds), plural_if("second", seconds)]
            
    if ago:
        stringParts.append("ago")
    
    return " ".join(stringParts)
    
def pretty_time_distance(za, zb):
    return pretty_timedelta(zb - za)

def pretty_time(ztime):
    return ztime.strftime("%A, %B %d, %Y @ %I:%M %p")
