class FatalVMCreationError(Exception):
    """
    Raised by BaseProvider.create_vm() if a virtual machine was partially
    created but some error prevented it from coming up completely. The
    partially created VM's ID will be queued for deletion when this exception
    is caught.

    :ivar vm_id: A `unicode` object containing the ID of the VM.

    """

    def __init__(self, vm_id):
        self.vm_id = vm_id

        super(FatalVMCreationError, self).__init__()

class BaseProvider(object):
    """
    The interface all providers should expose. This class should not be
    instantiated directly (and doing so may be made impossible at some point).

    .. note::

        This class does not provide any functionality but rather is meant as a
        documentation tool.

    """

    def __init__(self):
        pass

    def create_vm(self):
        """
        Creates a VM but does not prepare it.

        This should do the minimum amount of work necessary to allocate an ID
        for the VM and nothing more. All efforts should be made to keep this
        function from raising an exception because if any work is not yet done
        it will not be cleaned up. This means that this function should handle
        destroying a partially made virtual machine if it did not

        :returns: A `unicode` object containing the ID of the created VM.

        """

        pass

    def prepare_vm(self, vm_id):
        """
        Prepares a virtual machine with the given ID.

        After this function is called on a VM it should be completely ready to
        be handed over to a testrunner for use.

        :returns: None

        """

        pass

    def destroy_vm(self, vm_id):
        """
        Destroys a virtual machine with the given ID.

        :returns: None

        """

        pass
