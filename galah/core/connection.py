# The text banners here are useful for users of Sublime Text. They were
# generated with the Roman font at http://www.network-science.de/ascii/

class Connection:
    def __init__(self, **kwargs):
        pass

    # oooo  oooo   .oooo.o  .ooooo.  oooo d8b  .oooo.o
    # `888  `888  d88(  "8 d88' `88b `888""8P d88(  "8
    #  888   888  `"Y88b.  888ooo888  888     `"Y88b.
    #  888   888  o.  )88b 888    .o  888     o.  )88b
    #  `V88V"V8P' 8""888P' `Y8bod8P' d888b    8""888P'

    def user_lookup(self, current_user, handle, _hints = None):
        """
        Quickly looks up information on a specific user.

        :param handle: The user's *exact* handle.
        :type handle: unicode

        :returns: A User object or ``None`` if no user was found.

        """

        pass

    def user_multilookup(self, current_user, handles, _hints = None):
        """
        Quickly looks up information on a list of users.

        :param handles: A list of users' handles (must be exact like in
            user_lookup()).
        :type handles: list of unicode objects

        :returns: A list of User objects in no defined ordering. Any user that was
            not found will not appear in the list. If no users were found an empty
            list is returned.

        """

        pass

    def user_find(self, current_user, handle_starts_with = None, role = None,
            in_class = None, _hints = None):
        """
        Searches for users with particular parameters. If multiple criteria are
        provided only users that satisfy *all* criteria will be returned.

        TODO: Document parameters when they're finalized.

        :returns: A generator that yields User objects.

        """

        pass

    def user_create(self, current_user, new_user, _hints = None):
        """
        Creates a new user in the database. Raises an exception if user with the
        same handle exists.

        :param new_user: The user to add.
        :type new_user: User

        :returns: None

        """

        pass

    def user_update(self, current_user, updated_user, _hints = None):
        """
        Updates a user object in the database.

        :param updated_user: The user object containing the updated values.
        :type update_user: User

        :returns: None

        """

        pass

    def user_delete(self, current_user, handle, _hints = None):
        """
        Deletes a user object in the database.

        :param handle: The handle of the user to delete.
        :type handle: unicode

        :returns: None

        """

        pass

    #           oooo
    #           `888
    #  .ooooo.   888   .oooo.    .oooo.o  .oooo.o  .ooooo.   .oooo.o
    # d88' `"Y8  888  `P  )88b  d88(  "8 d88(  "8 d88' `88b d88(  "8
    # 888        888   .oP"888  `"Y88b.  `"Y88b.  888ooo888 `"Y88b.
    # 888   .o8  888  d8(  888  o.  )88b o.  )88b 888    .o o.  )88b
    # `Y8bod8P' o888o `Y888""8o 8""888P' 8""888P' `Y8bod8P' 8""888P'

    def class_lookup(self, current_user, class_id, _hints = None):
        """
        Quickly looks up information on a particular class.

        :param class_id: The ID of the class to lookup.
        :type class_id: Class.ID

        :returns: A Class or None if no matching class was found.

        """

        pass

    def class_multilookup(self, current_user, class_ids, _hints = None):
        """
        Quickly looks up information on a number of different classes.

        :param class_ids: A list of class ids (must be exact like in
            user_lookup()).

        :returns: A list of Class objects in no defined ordering. Any class that
            was not found will not appear in the list. If no classes were found an
            empty list is returned.

        """

        pass

    def class_find(self, current_user, term, handle_starts_width, _hints = None):
        pass

    def class_create(self, current_user, new_class, _hints = None):
        pass

    def class_update(self, current_user, updated_class, _hints = None):
        pass

    def class_delete(self, current_user, id, _hints = None):
        pass

    #  .oooo.    .oooo.o  .oooo.o  .oooooooo ooo. .oo.
    # `P  )88b  d88(  "8 d88(  "8 888' `88b  `888P"Y88b
    #  .oP"888  `"Y88b.  `"Y88b.  888   888   888   888
    # d8(  888  o.  )88b o.  )88b `88bod8P'   888   888
    # `Y888""8o 8""888P' 8""888P' `8oooooo.  o888o o888o
    #                             d"     YD
    #                             "Y88888P'

    def assignment_lookup(self, current_user, assignment_id, _hints = None):
        pass

    def assignment_find(self, current_user, for_classes = None, _hints = None):
        pass

    def assignment_create(self, current_user, new_assignment, _hints = None):
        pass

    def assignment_delete(self, current_user, id, _hints = None):
        pass

    #                       .o8
    #                      "888
    #  .oooo.o oooo  oooo   888oooo.   .oooo.o
    # d88(  "8 `888  `888   d88' `88b d88(  "8
    # `"Y88b.   888   888   888   888 `"Y88b.
    # o.  )88b  888   888   888   888 o.  )88b
    # 8""888P'  `V88V"V8P'  `Y8bod8P' 8""888P'

    def submission_lookup(self, current_user, submission_id, _hints = None):
        pass

    def submission_find(self, current_user, author = None, for_assignment = None,
            _hints = None):
        pass

    def submission_create(self, current_user, new_submission, _hints = None):
        pass

    def submission_update(self, current_user, updated_submission, _hints = None):
        pass

    def submission_delete(self, current_user, submission_id, _hints = None):
        pass

    #   .o8                        .o8
    # .o888oo  .ooooo.   .oooo.o .o888oo oooo d8b  .ooooo.   .ooooo oo  .oooo.
    #   888   d88' `88b d88(  "8   888   `888""8P d88' `88b d88' `888  d88(  "
    #   888   888ooo888 `"Y88b.    888    888     888ooo888 888   888  `"Y88b.
    #   888 . 888    .o o.  )88b   888 .  888     888    .o 888   888  o.  )88
    #   "888" `Y8bod8P' 8""888P'   "888" d888b    `Y8bod8P' `V8bod888  8""888P
    #                                                             888.
    #                                                             8P'
    #                                                             "

    def testrequest_lookup(self, current_user, testrequest_id, _hints = None):
        pass

    def testrequest_pop(self, current_user, _hints = None):
        pass

    def testrequest_create(self, current_user, new_testrequest, _hints = None):
        pass

    def testrequest_delete(self, current_user, testrequest_id, _hints = None):
        pass

    #                                         oooo      .
    #                                         `888    .o8
    # oooo d8b  .ooooo.   .oooo.o oooo  oooo   888  .o888oo  .oooo.o
    # `888""8P d88' `88b d88(  "8 `888  `888   888    888   d88(  "8
    #  888     888ooo888 `"Y88b.   888   888   888    888   `"Y88b.
    #  888     888    .o o.  )88b  888   888   888    888 . o.  )88b
    # d888b    `Y8bod8P' 8""888P'  `V88V"V8P' o888o   "888" 8""888P'

    def testresult_lookup(self, current_user, testresult_id, _hints = None):
        pass

    def testresult_find(self, current_user, for_submission = None, for_user = None,
            for_assignment = None, _hints = None):
        pass

    def testresult_create(self, current_user, new_testresult, _hints = None):
        pass

    def testresult_update(self, current_user, updated_testresult, _hints = None):
        pass

    def testresult_delete(self, current_user, testresult_id, _hints = None):
        pass


    #     .                      oooo
    #   .o8                      `888
    # .o888oo  .oooo.    .oooo.o  888  oooo   .oooo.o
    #   888   `P  )88b  d88(  "8  888 .8P'   d88(  "8
    #   888    .oP"888  `"Y88b.   888888.    `"Y88b.
    #   888 . d8(  888  o.  )88b  888 `88b.  o.  )88b
    #   "888" `Y888""8o 8""888P' o888o o888o 8""888P'

    def task_lookup(self, current_user, task_id, _hints = None):
        pass

    def task_create(self, current_user, new_task, _hints = None):
        pass

    def task_pop(self, current_user, action, _hints = None):
        pass

    def task_delete(self, current_user, task_id, _hints = None):
        pass
