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

    @staticmethod
    def get_mine():
        """Returns the current node's NodeID."""

        return NodeID(u"a", u"b")
