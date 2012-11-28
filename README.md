# Galah

**Documentation for galah.api available at https://galah-api.readthedocs.org/en/latest/!**

## What is Galah?

Galah is a teaching utility that automatically analyzes students' code as
they create it and provides feedback to both the students and the instructors.
It does this by continually running tests on students' code and providing the
results to both the instructors and the students.

Professors are responsible for creating test harnesses for their assignments,
aside from that Galah does the rest of the work: running those tests inside of
a secure VM; consolodating results into a database; and providing an interface
for the students and teachers to see the results of the testing.

### Current Status

The latest version of Galah only works as a submission system. Testing is not
performed.

## License

Galah's source code AND documentation are licensed under the GNU AGPLv3. A
textual copy of the AGPLv3 is included in the file LICENSE.

### Considerations

The AGPLv3 is basically the GPLv3 with an added restriction aimed towards
server software like Galah. To best know your rights, you should read and
understand the entirety of the AGPLv3, however, below is a basic run through of
what you should keep in mind when using Galah. Note that it is not legally
binding text and does not supersede the AGPLv3.

Because Galah's source code and documentation are licensed under the GNU AGPLv3,
you must always provide a link to a freely available copy of the currently
running source code to anybody who interacts with your deployed version of
Galah. In fewer words, leave the footer that's included in every page intact,
and if you make changes to the source code, make sure to host your changes on
GitHub and configure Galah to link the "Get the code!" link to your public repo.

Test harnesses you create, code your students submit, and configuration files
you create are not owned by Galah's contributers therefore the AGPLv3 does not
apply to them. So you do not have to make your test harnesses freely available
to your students (don't worry!). 

The documentation's "source code" is the reStructuredText included in this repo,
the documentation's "object code" is the HTML, MAN, or other formatted output
that sphinx (or whatever program your using) generates. So if you make
modifications to the documentation and distribute or host a "compiled" version
of the documentation (so an HTML, MAN, or other version), you must provide a
link to the reStructuredText version of the source code **in the documentation**
(note that modifying galah's configuration file will not modify the output of
the documentation, you must do that manually in the `index.rst` file). It is
reccomended that you just do the same thing as if you had made modifications to
Galah's core source code (legally you basically did) and put up a GitHub repo
with your changes.

## Informal Credits and Contributors

This is an informal list of contributers and those who gave me assistance during
Galah's development. For the list of contributers who have copyright claims to
Galah or pieces of Galah please refer to the CONTRIBUTERS file.

Thank you all of you!

### Ben Kellogg

Helped considerably with galah.sheep, wouldn't have been able to finish it
without him.

### UCR Staff & Faculty

Victor Hill, Kris Miller and Brian Linard have all been
enormously helpful in getting Galah off the ground and into production.
That's not even mentioning the other staff and faculty at UCR who have
shared their knowledge with me. Thank you everyone who has helped me grow
as a software engineer.

Victor Hill was also the one who initially concieved of Galah, I just
implemented it.

### Christopher Johnson

Has a very nice site at www.chris.com that I got some ASCII birds from. I would
like to grab some more in the future so the error pages can generate a random
ASCII bird every time you go them. Now error pages are fun too!

### Chris Manghane

Implemented Galah's support for Google OAuth2.

## News

### Monday, June 25, 2012

Changing version scheme to something a little less ridiculous. I don't really
know what my version scheme was before but now I'll follow more standard
conventions. MajorVersion.MinorVersion.Patch[rc#], in other words what you'd
expect. I will refer to the previous release 0.1beta1 as 0.1rc1 from now on.
The next "release" will be 0.1rc2. When I feel confident that a lot of the
bugs are worked out we'll release 0.1.

Each component of Galah is pretty distinct and decoupled from the other
componenets of Galah but I don't want to make multiple repositories for each
unless each one grows very large in size (which they shouldn't), so there
won't be seperate versioning for each component.

### Sunday, June 24, 2012

Version 0.1beta1 has been released. This release contains only galah.web and
galah.db running without support for interacting with the testing backend. All
functionality needed for deploying in a production environment is there and
most of it is documented.

Exciting day today :).
