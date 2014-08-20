from galah.base.magic import memoize

@memoize
def get_virtual_suite(suite_name):
    suite_name = suite_name.lower()

    if suite_name == "openvz":
        import galah.sheep.virtualsuites.vz as vz
        return vz
    elif suite_name == "dummy":
        import galah.sheep.virtualsuites.dummy as dummy
        return dummy
    else:
        raise ValueError("Suite name %s not recognized." % suite_name)
