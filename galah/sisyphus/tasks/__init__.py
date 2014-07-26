# Copyright (c) 2012-2014 John Sullivan
# Copyright (c) 2012-2014 Chris Manghane
# Licensed under the MIT License <http://opensource.org/licenses/MIT>

from zip_bulk_submissions import _zip_bulk_submissions
from delete_assignments import _delete_assignments
from create_assignment_csv import _create_assignment_csv
from create_gradebook_csv import _create_gradebook_csv
from rerun_test_harness import _rerun_test_harness

task_list = {
    "zip_bulk_submissions": _zip_bulk_submissions,
    "delete_assignments": _delete_assignments,
    "create_assignment_csv": _create_assignment_csv,
    "create_gradebook_csv": _create_gradebook_csv,
    "rerun_test_harness": _rerun_test_harness
}
