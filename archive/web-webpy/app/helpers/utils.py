import config

# !!! Import statement at bottom

def shallowFlatten(zlist):
    "Flattens a list of lists."
    
    # Courtesy: http://stackoverflow.com/a/952952
    return [item for sublist in zlist for item in sublist]

def first(zlist, zpredicate):
    "Finds the first item in an iterable where zpredicate(item) is true."
    
    return next(i for i in zlist if zpredicate(i))

def renderScore(zobject):
    convert = lambda d: str(d) if str(d)[-2:] != ".0" else str(d)[:-2]
    
    if not zobject.score:
        return "Inconclusive"
    else:
        return "%s / %s" % (convert(zobject.score),
                            convert(zobject.maxScore))

def safeStrCmp(za, zb):
    if len(za) != len(zb):
        return False
    
    rv = True
    for x, y in zip(za, zb):
        if x != y:
            rv = False
    
    return rv
    
class HashInfo:
    "Utility class for dealing with hashed passwords in the database."
    
    def __init__(self, zalgorithm = "", zsalt = "", zcostFactor = 0, zhash = ""):
        self.algorithm = str(zalgorithm)
        self.salt = str(zsalt)
        self.costFactor = int(zcostFactor)
        self.hash = str(zhash)
    
    def hashString(self, zstr):
        """
        Hashes a string given the algorithm, salt, and costFactor for this
        object.
        
        """
        
        assert self.algorithm == "PBKDF2-256"
        
        return pbkdf2.pbkdf2_hex(str(zstr), str(self.salt), self.costFactor)
    
    @classmethod
    def fromString(cls, zstring):
        "Deconstructs a string into a PassInfo object"
        
        # Create a new instance
        obj = cls()
        
        # Deconstruct the string
        passInfo = zstring.split(":")

        # Fill in the datamembers
        obj.algorithm = str(passInfo[0])
        obj.salt = str(passInfo[1])
        obj.costFactor = int(passInfo[2])
        obj.hash = str(passInfo[3])
        
        return obj
    
    def __str__(self):
        return ":".join((self.algorithm, self.salt, str(self.costFactor), self.hash))

def isLocalUrl(zurl):
    "Returns true iff the URL points to a location on this web server"
    
    if not zurl or zurl == "#":
        return True
    
    if zurl.startswith("http://" + config.siteAddress):
        return True
    elif zurl[0].isalnum() or zurl[0] == "/" or zurl[0]:
        return True
        
    return False
            
# Thanks to http://norvig.com/python-iaq.html
class Enum:
    """Create an enumerated type, then add var/value pairs to it.
    The constructor and the method .ints(names) take a list of variable names,
    and assign them consecutive integers as values.    The method .strs(names)
    assigns each variable name to itself (that is variable 'v' has value 'v').
    The method .vals(a=99, b=200) allows you to assign any value to variables.
    A 'list of variable names' can also be a string, which will be .split().
    The method .end() returns one more than the maximum int value.
    Example: opcodes = Enum("add sub load store").vals(illegal=255)."""
  
    def __init__(self, names=[]): self.ints(names)

    def set(self, var, val):
        """Set var to the value val in the enum."""
        if var in vars(self).keys(): raise AttributeError("duplicate var in enum")
        if val in vars(self).values(): raise ValueError("duplicate value in enum")
        vars(self)[var] = val
        return self
  
    def strs(self, names):
        """Set each of the names to itself (as a string) in the enum."""
        for var in self._parse(names): self.set(var, var)
        return self

    def ints(self, names):
        """Set each of the names to the next highest int in the enum."""
        for var in self._parse(names): self.set(var, self.end())
        return self

    def vals(self, **entries):
        """Set each of var=val pairs in the enum."""
        for (var, val) in entries.items(): self.set(var, val)
        return self

    def end(self):
        """One more than the largest int value in the enum, or 0 if none."""
        try: return max([x for x in vars(self).values() if type(x)==type(0)]) + 1
        except ValueError: return 0
    
    def getName(self, zvalue):
        for k, v in vars(self).items():
            if v == zvalue:
                return k
                
        raise KeyError("value %s not found" % zvalue)
    
    def __getitem__(self, key):
        return vars(self)[key]
        
    def __setitem__(self, key, val):
        self.set(key, val)
    
    def _parse(self, names):
        ### If names is a string, parse it as a list of names.
        if type(names) == type(""): return names.split()
        else: return names

def selectFromDict(zdict, zpredicate):
    for k, v in zdict.items():
        if zpredicate(k, v):
            yield (k, v)

# Imported down here to avoid circular dependency
from app.helpers import pbkdf2
