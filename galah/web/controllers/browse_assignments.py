from galah import core

def browse_assignments():
    current_user = get_current_user()

    # Grab all of the current user's classes
    classes = core.class_multilookup(
        current_user.classes,
        _hints = {
            "only-fields": ["name"]
        }
    )

    # Get the current time so we don't have to do it over and over again.
    now = datetime.datetime.today()

    # If an assignments due or cutoff date is after this point it will be
    # shown.
    show_after = now - datetime.timedelta(week = 1)

    # Grab initially all of the assignments for all the classes the student
    # is enrolled in due or cutoff after some time frame.
    assignments = core.assignment_find(
        for_classes = current_user.classes,
        _hints = {
            "after": show_after
        }
    )

    if current_user.personal_deadlines:
        desired_assignments = [
            i[0] for i in current_user.personal_deadlines.items() if
                i[1].hide_until < now and
                i[1].due > show_after and
                i[1].cutoff > show_after
        ]

        # Create a set we can use to efficiently check what assignments we've
        # grabbed already from our call to assignment_find above.
        retrieved_assignments = set(i.id for i in assignments)
