"""
This module contains objects that are a part of the galah.core API. As such,
they are backend agnostic and suitable for passing in and out of core
functions.

"""

# external
from mangoengine import *

class BackendError(RuntimeError):
    pass

class NodeID(Model):
    """
    A node is a single application such as a vmfactory or webapp process.

    :ivar machine: A unicode string identifying the machine the node is running
        on. The System Administrator can set this to whatever makes the most
        sense to them (hostname, IP address, nickname ...).
    :ivar local: An integer uniquely identifying the application on its
        machine. This is part of the ID is automatically allocated.

    """

    machine = UnicodeField()
    local = IntegralField(bounds = (0, None))

    def serialize(self):
        """
        Returns a string representation of this NodeID that can be passed to
        deserialize() later.

        .. note::

            Validation is performed before serializing by calling the
            validate() function.

        :returns: A UTF-8 encoded string (not a ``unicode`` instance however).

        """

        # Our serialized string may not be capable of being deserialized if
        # machine and local aren't valid so we validate inside the function.
        self.validate()

        return "%s:%d" % (self.machine.encode("utf_8"), self.local)

    @classmethod
    def deserialize(cls, string):
        """
        Returns the NodeID object serialized in string.

        .. note::

            The result is validated before being returned by calling the
            validate() function.

        :param string: A UTF-8 string as provided by serialize().

        :returns: A NodeID instance.

        """

        for i in xrange(0, len(string)):
            if string[len(string) - i - 1] == ":":
                break
        else:
            raise ValueError("string %s is not a serialized NodeID" %
                (repr(string), ))

        local = int(string[len(string) - i:])
        machine = string[:len(string) - i - 1].decode("utf_8")

        result = cls(machine = machine, local = local)
        result.validate()

        return result
