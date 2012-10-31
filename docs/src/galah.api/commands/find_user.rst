find_user
=========

Finds users matching the given credentials

Reference
---------

.. function:: find_user([email_contains = "", account_type = "", enrolled_in = ""])
    
    :param email_contains: Part of the email to match
    
    :param account_type: The user's account type

    :param enrolled_in: A class the user is enrolled in. You can specify the
                        name of the class or the ID of the class.

Example Usage
-------------

When called without parameters, :func:`find_user` lists all users that Galah
recognizes.

>>> find_user
--Logged in as jsull003@ucr.edu--
3 user(s) found matching query {any}.
    User [email = jsull003@ucr.edu, account_type = admin]
    User [email = eadel002@ucr.edu, account_type = student]
    User [email = test@school.edu, account_type = student]

We will search for all student users that Galah recognizes.

>>> find_user "" student
--Logged in as jsull003@ucr.edu--
2 user(s) found matching query {account type is 'student'}.
    User [email = eadel002@ucr.edu, account_type = student]
    User [email = test@school.edu, account_type = student]

Now we will search for all students in the class **CS 9000**.

>>> find_user "" student "CS 9000"
--Logged in as jsull003@ucr.edu--
2 user(s) found matching query {account type is 'student',enrolled in Class [id = 5090634855c448134f67b3e3, name = CS 9000]}.
    User [email = eadel002@ucr.edu, account_type = student]
    User [email = test@school.edu, account_type = student]