# Galah

### Current Status

Version 0.1 is stable and ready to be used within a production environment.
It is only a submissions system however, the automatic testing functionality
of Galah will be added in version 0.2.

## What is Galah?

Galah is a teaching utility that automatically analyzes students' code as
they create it and provides feedback to both the students and the instructors.
It does this by continually running tests on students' code and providing the
results to both the instructors and the students.

Professors are responsible for creating test harnesses for their assignments,
aside from that Galah does the rest of the work: running those tests inside of
a secure VM; consolodating results into a database; and providing an interface
for the students and teachers to see the results of the testing.

### Documentation and Getting Started

Documentation for Galah is maintained on the
[GitHub project's wiki](https://github.com/brownhead/galah/wiki).

## News

### Wednesday, December 5, 2012

Version 0.1 has been released and is going into deployment at UCR :D. Any bug
fixes to the current code will be committed to master and releases will be made
following the pattern 0.1.RELEASE#, so the first bug fix release will be 0.1.1,
and the thirteenth would be 0.1.13.

A new branch will be created named v0.2dev and development towards the 0.2
release will proceed there. Bug fixes made in master will be merged into that
branch.

Release date for version 0.2 is unknown, not even a hunch at this point.

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
