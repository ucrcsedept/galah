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
        destroying a partially made virtual machine if it did not finish
        creating it.

        :returns: The metadata that should be associated with the VM as a
            dictionary.

        """

        pass

    def prepare_vm(self, vm_id, set_metadata, get_metadata):
        """
        Prepares a virtual machine with the given ID.

        After this function is called on a VM it should be completely ready to
        be handed over to a testrunner for use. This typically involves
        installing the bootstrapper server onto the vm.

        :param vm_id: The NodeID of the VM.
        :param set_metadata: A function ``set_metadata(key, value)`` that can
            be called to set metadata related to the VM.
        :param get_metadata: A function ``get_metadata(key)`` that can be called
            to get metadata related to the VM.

        :returns: None

        """

        pass

    def destroy_vm(self, vm_id, get_metadata):
        """
        Destroys a virtual machine with the given ID.

        :param vm_id: The NodeID of the VM.
        :param get_metadata: A function ``get_metadata(key)`` that can be called
            to get metadata related to the VM.

        :returns: None

        """

        pass

    def recover_vms(self):
        """
        Goes through all of the Galah-created VMs on the machine and determines
        whether they are clean or dirty using no additional information.

        :returns: A tuple ``(clean_vms, dirty_vms)`` where each item is a
            list of dictionaries containing the meta-data about each VM that
            could be garnished from local sources.

        """

        pass
