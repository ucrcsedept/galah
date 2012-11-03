create_user
===========

Creates a user with the given credentials. Be very careful executing this
API as the password may be momentarilly visible in a ps listing. Ensure you
are in a secure terminal.

Also, if the Galah webserver is not set up to use HTTPS, you should take
effort to make sure you're on the same network as Galah, because **the
password will be sent as plaintext**.

Reference
---------

.. function:: create_user(email, password[, account_type = 'student'])

    :param email: The email the user will use to sign in.
    
    :param password: The users password, it will be immediately hashed.

    :param account_type: The account type. Current available options are
                         student, teacher, or admin. Multiple account types are
                         not legal.

Example Usage
-------------

Creating a student named **test@school.edu** with the password
**gReatPassWord**.

>>> create_user test@school.edu gReatPassWord
--Logged in as jsull003@ucr.edu--
Success! User [email = test@school.edu, account_type = student] created.
