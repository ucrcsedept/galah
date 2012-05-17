import json
import inspect
from types import NoneType

def UpdateFromDictionary(zdictionary, zobject):
    """
    Treats zdictionary as a Javascript object of sorts and tries to update
    zobject (a python object) with the values from zdictionary and makes sure
    types and datamembers match.
    
    Example: If zdictionary = {'a': 12, 'b' = 'hi', 'c' = {'d' = 1}} and
    zobject's datamembers are {'a': None, 'b' = '', 'c' = {}} this function
    will transfer all the data as expected, but if attribute a in zobject had
    equaled "" this function would have thrown an ValueError.
    
    zobject may either be a class (in which case a new instance will be
    created within the function) or an instance of a class.
    
    """
    
    if inspect.isclass(zobject):
        zobject = zobject()
    
    for name, value in zobject.__dict__.iteritems():
        if name not in zdictionary:
            raise ValueError("Missing attribute in source.")
            
        # Check if the 
        if type(value) not in (dict, list, set, range, xrange, str, int,
                               float, long, complex, NoneType):
            if type(value) is not dict:
                raise TypeError("Type mismatch in source.")
        
        if value is not None and \
                not isinstance(type(zdictionary[name]), type(value)):
            raise TypeError("Type mismatch in source.")
        
        zobject.__dict__[name] = zdictionary[name]
