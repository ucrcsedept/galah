Using Vagrant with Galah
========================

Vagrant will automatically create and give you access to a virtual machine that has been prepared for development with Galah. In order to use Vagrant, you must install a few programs:

 * `Vagrant <http://www.vagrantup.com/downloads.html>`_
 * `Ansible <http://docs.ansible.com/intro_installation.html>`_
 * `VirtualBox <https://www.virtualbox.org/wiki/Linux_Downloads>`_

Then you will need to retrieve the appropriate Galah Vagrant Box (**instructions not yet available for this step**).

Finally, you should navigate to the appropriate directory in ``install/vagrant/`` (which is a directory in the Galah core git repo) and run the command ``vagrant up``. After Vagrant is finished setting up the VM you will be able to run ``vagrant ssh`` to enter the virtual machine and begin development.

Troubleshooting
---------------

Mismatched Guest Additions Version
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you receive an error like the following...

```text
[default] The guest additions on this VM do not match the installed version of
VirtualBox! In most cases this is fine, but in rare cases it can
cause things such as shared folders to not work properly. If you see
shared folder errors, please update the guest additions within the
virtual machine and reload your VM.

Guest Additions Version: 4.3.6
VirtualBox Version: 4.2
```

Either your version of VirtualBox is out-of-date in which case you should upgrade, or the version of Guest Additions is out-of-date, in which case you should download a new box, or create a new one with Packer.
