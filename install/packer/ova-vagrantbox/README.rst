Vagrant Box Creator
===================

This will create a Vagrant Box out of an already created virtual machine image. You must provide an OVA file named ``source.ova`` and it must be in the same directory as the ``packer-config.json`` file.

Fact Sheet
----------

 * Output OVA file will be in ``output-virtualbox-ovf/`` directory
 * User ``vagrant`` with SSH access through keys available `here <https://github.com/mitchellh/vagrant/tree/a91edab59194141b01b21602247ca9a1f2bb1953/keys>`_ (has passwordless sudo access)
 * Login with user ``root`` password ``packer``
