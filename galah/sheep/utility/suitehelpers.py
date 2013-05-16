# Copyright 2012 John Sullivan
# Copyright 2012 Other contributors as noted in the CONTRIBUTORS file
#
# This file is part of Galah.
#
# Galah is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Galah is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Galah.  If not, see <http://www.gnu.org/licenses/>.

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