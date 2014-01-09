# stdlib
import uuid

# external
from mangoengine import *

from galah.base.config import load_config
config = load_config("core")

import logging
log = logging.getLogger("galah.core.redis")

class NodeID(Model):
    machine = UnicodeField()
    """A unique ID for the machine the node is running on."""

    local = UnicodeField()
    """
    A unique ID for the actual application. Only needs to be unique to the
    machine.

    """

    @classmethod
    def get_mine(cls):
        """Returns the current node's NodeID."""

        if hasattr(cls, "_saved_local_id"):
            local = cls._saved_local_id
        else:
            # We always generate a new ID rather than reading it from a file
            cls._saved_local_id = local = uuid.uuid4()

        if hasattr(cls, "_saved_machine_id"):
            machine = cls._saved_machine_id
        else:
            # TODO: This should make a peristant ID on the filesystem.
            cls._saved_machine_id = machine = uuid.uuid4()

        return cls(machine = machine, local = local)

    def __str__(self):
        return "%s::%s" % (self.machine, self.local)
