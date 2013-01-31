# Galah

## What is Galah?

Galah is an automated grading system geared towards processing computer
programming assignments.

Professors are responsible for creating test harnesses for their assignments.
Aside from that Galah does the rest of the work: running those tests inside of
secure Virtual Machines, consolodating results into a database, and providing an
interface for the students and teachers to see the results of the testing.

Galah aims to set itself apart from similar software suites by being
language agnostic, scalable, secure, easy to use, and simple
([more on Galah's goals](https://github.com/brownhead/galah/wiki/Goals-and-Ideals)). Check
out this
[comparison to similar software](https://github.com/brownhead/galah/wiki/Comparison-to-Similar-Software).

## Documentation and Getting Started

Documentation for Galah is maintained on the
[GitHub project's wiki](https://github.com/brownhead/galah/wiki). This
documentation is meant to be useful to users of Galah, interested parties
looking to see if Galah would be useful to them, and developers.

## Current Status

Version 0.1 is stable and ready to be used within a production environment. This
first version is only a submission system and does not perform any testing on
student's code.

Version 0.2 is unstable but highly useable (and is being used already).

## News

### Wednesday, January 30, 2013

A rapid release cycle has started on the version 0.2 branch.
[Galah has been deployed at UCR](https://galah.cs.ucr.edu) and the full
auto-testing functionality is being used. This week we had the first series of
labs taking advantage of Galah and it went very well. Students seemed to
appreciate the quickness and quality of the feedback they got. We'll be using
the feedback from this round of labs and improving things appropriately.

We're on track for a stable 0.2 release by the time the next quarter start.

### Wednesday, December 5, 2012

Version 0.1 has been released and is going into deployment at UCR :D. Any bug
fixes to the current code will be committed to master and releases will be made
following the pattern 0.1.RELEASE#, so the first bug fix release will be 0.1.1,
and the thirteenth would be 0.1.13.

A new branch will be created named v0.2dev and development towards the 0.2
release will proceed there. Bug fixes made in master will be merged into that
branch.

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
