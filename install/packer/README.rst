How to Build Galah's VM Images
==============================

You must have `Packer <http://packer.io>`_ and `Virtual Box <https://www.virtualbox.org/>`_ installed in order to build the VM images.

Once packer is installed, **change into the directory** containing the configuration of the image you would like to generate and run ``packer build packer-config.json``.

There may be additional set up required (such as moving any source OVA files into the directory) so make sure to check the README in the configuration directory as well.
