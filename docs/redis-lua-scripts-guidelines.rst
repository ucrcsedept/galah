Redis Lua Scripting Guidelines
==============================

Complex, atomic transactions in Redis can be performed by sending the Redis server Lua scripts. We do this extensively within ``galah.core.redis``. This document describes some best practices to follow when creating these scripts so some manner of consistency is maintained.

The ``redis-scripts.lua`` File
------------------------------

Rather than inlining the Lua scripts in the Python code, or maintaining a large directory of Lua scripts, we keep all of the scripts inside of a single file located at ``galah/core/redis-scripts.lua``. This file contains a number of scripts, all in the following format.

```lua
----script core_function_using_this:name_of_script

local some = "lua code"
return some
```

The ``RedisConnection.__init__()`` function will parse this file and register all of the scripts with the server when a connection is made.

Return Values
-------------

Each script returns a particular value that is then interpreted by Galah. There are a number of `data types <http://redis.io/topics/protocol#status-reply>`_ that Redis supports (`rules for converting between Lua and Redis data types <http://redis.io/commands/EVAL>`_). When writing your own Lua scripts, try your best to follow the guidelines below:

 * If there is an error condition that does not revolve around an actual Redis
   syntax error, return a negative integer.
 * Use ``redis.call()`` so that Redis errors are propagated up through the
   script and to the application.
 * If it makes sense, use 0 for False and 1 for True.

Beyond these guidelines, use your best judgement to make an API that makes sense. And of course, make sure to well comment the code and document the functions to the best of your ability.
