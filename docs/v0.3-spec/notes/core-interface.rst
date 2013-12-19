Currently (and into the foreseeable future) there is only a couple services the core needs to communicate with. A database and a queue (since most databases also have queuing abilities the second could be optional). Knowing this, how should we organize the core's codebase? A tricky thing to deal with is that the combination of mongo and redis for example may have different code than mongo and some other queue. A way to solve this could be to completely lock Galah into Redis.

This is not ideal but not horrible, as it's unlikely we'd want to use a different queueing solution like Rabbit. It is possible though that a team may not want to use a queue at all but instead just use the database, and I don't really want to disallow that at a layer as difficult to change as the public interface... What is the interface anyway...

Optimizations
-------------

There are many different optmizations that are useful when querying the database. Such as limiting the fields you are returned, or limiting the number of items the database looks for. The public interface should not explicitly expose such optimizations as parameters, instead they should be passed in as a dictionary of "hints" which may or may not be used by the underlying implementation.

Users
-----

There are a couple notable changes to users. Firstly, the ``email`` field has been replaced with ``handle``. A user's handle may be anything (and in fact can still be their email). Secondly, ``account_type`` has been replaced with a list of roles.

Classes
-------

A class now has a term and a handle where the term and handle can both be arbitrary strings but neither can be the empty string. Term is expected to relate to some time period and will be used when presenting classes to users based on that assumption. Handle is expected to be the name of the class. The old ``name`` field no longer exists.

A class still has an ID and its ID is used to reference classes internally, so terms and handles can be changed without expensive updates.

Tasks
-----

The task runners will be responsible for all of sisyphus's jobs and a little more. They will receive messages through the core. A task will have an action and a dictionary of arbitrary meta-data.

Archives
~~~~~~~~

Archives will be created by the task runners rather than the web servers. The user will be sent to a URL and once they go there Nginx or Apache will keep them waiting until a file appears that matches the name. Security will be handled by a suitably high entropy randomized directory name (will not actually use directories though if we can avoid it but will instead have nginx or apache do the resolution).
