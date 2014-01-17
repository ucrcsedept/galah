"""
This module contains objects that are a part of the galah.core API. As such,
they are backend agnostic and suitable for passing in and out of core
functions.

"""

# external
from mangoengine import *

class CoreError(RuntimeError):
    """
    An error thrown by galah.core.

    """

    pass

class BackendError(CoreError):
    """
    Raised when an error occurs in the backend. This class is never
    instantiated directly but rather is inherited from.

    """

    pass

class IDNotRegistered(CoreError):
    """
    Raised when a provided ID (such as a NodeID) was not found in the backend.
    This will most likely occur when trying to perform operations as an
    unregistered user or with an unregistered node.

    """

    def __init__(self, unregistered_id):
        self.unregistered_id = unregistered_id

    def __str__(self):
        return "Unregistered id '%s'" % (self.unregistered_id.serialize(), )

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

    def __str__(self):
        # This is to give us a little bit of type-checking goodness where
        # NodeID's are serialized because it forces us to use .serialize()
        # rather than just using str() which will work on nearly every type.
        raise TypeError("__str__ is not supported for NodeID objects.")

    # Other core objects should not necessarily have a serialize function. If
    # the object can be stored as JSON use a JSON serializer directly instead.
    # The NodeID needs to be serialized a particular way thus these functions.
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

