CHANGELOG for LaunchKey Python SDK
==================================

3.1.1
-----

* Added patch method for transports
* Support for many new endpoints added involving Organization, Directory, and Service management
* Moved all entity objects into their own submodule
* Added UUID validation for factory entity IDs

3.0.2
-----

* Improved 401 error handling
* Bug fix for SessionEndRequest object
* Service PINs bug fix

3.0.1
-----

* Typo and manifest fixes
* Added Unauthorized status code error handler
* Nose version lock for test requirements

3.0.0
-----

* Complete revamp for new V3 LaunchKey API

2.0.1
-----

* Make tests run under Python 3.5+
* Make PEP-8 compliant (deprecated some non-PEP-8 compliant functions)

1.3.0
-----

* Python 3 compatibility.
* Ability to send policies in auth request.

1.2.7
-----

* Update manifest for new CHANGES file

1.2.6
-----

* Fix for bad build regarding CHANGES.md

1.2.5
-----

* Remove references to LK Identifier as the API no longer returns it.