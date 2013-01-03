# Changelog

Please consult this file before updating to a new version of Galah in case there
are pertinent *Upgrading Considerations* that you should be aware of. Also, make
sure to look over the guide for
[updating Galah](https://github.com/brownhead/galah/wiki/Updating-Galah).

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