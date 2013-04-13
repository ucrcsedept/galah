# Copyright 2012-2013 John Sullivan
# Copyright 2012-2013 Other contributers as noted in the CONTRIBUTERS file
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

from tar_bulk_submissions import _tar_bulk_submissions
from delete_assignments import _delete_assignments
from create_assignment_csv import _create_assignment_csv
from rerun_test_harness import _rerun_test_harness

task_list = {
	"tar_bulk_submissions": _tar_bulk_submissions,
        "delete_assignments": _delete_assignments,
        "create_assignment_csv": _create_assignment_csv,
        "rerun_test_harness": _rerun_test_harness
}
