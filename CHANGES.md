# Changelog

Please consult this file before updating to a new version of Galah in case there
are pertinent *Upgrading Considerations* that you should be aware of. Also, make
sure to look over the guide for
[updating Galah](https://github.com/brownhead/galah/wiki/Updating-Galah).

## Version 0.1.3

Made `create-admin.py` more accessible from scripts and improved on documentation based on user feedback.

### Changes

 * `create-admin.py` received an overhaul. Run create-admin.py to see its new interface. It is not backwards compatible with the old interface so be wary! Now you must specify at least one command line argument.
 * Added 2013 to the copyright headers for this release. Every file was touched so don't be surprised if your `git pull` brings in more than you bargained for.
 * Init scripts and documentation has been improved. Glance through the changes on the wiki for more details.

### Upgrading Considerations

If you use `create-admin.py` from a script (though it's unlikely you were able to), you will have to modify that script to accomadate the new interface.

## Version 0.1.2

Couple of bug fixes, one fairly major.

### Changes

 * The submissions were not being sorted properly on the view assignment page.
 * Fixed bug that caused many API commands to fail.

### Upgrading Consideratinos

None.

## Version 0.1.1

Small patch for an update to one of Galah's dependencies.

### Changes

 * Very low priority security patch.
 * Added support for requests 1.x, dropped support for 0.x.

### Upgrading Considerations

The dependency [requests](http://pypi.python.org/pypi/requests) will be updated.
This may affect other programs on your system.