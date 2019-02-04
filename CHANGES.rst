CHANGELOG for LaunchKey Python SDK
==================================

3.4.0
-----

* Added ttl parameter to the DirectoryClient link_device method
* Added cancel_authorization_request method to the ServiceClient

3.3.0
-----

* Added tooling around code quality and ensured that CI build would fail without meeting expectations.
* Added dynamic auth TTL and title functionality
* Added dynamic auth push message body and title functionality
* Added auth busy signal error handling
* Added new auth response format
* Added auth denial context functionality

3.2.0
-----

* Remove PyCrypto and replace with pycryptodomex that is already required by PyJWKEST
* Fixed geofence missing name bug
* Added more expected error conditions to pydocs
* Removed version lock for pytz requirement
* Added 3rd party push enhancements
* Added tox config for local testing in multiple versions of Python
* Added missing response validation
* Added full webhook validation
* Cleaned up error handling and raising for webhooks
* Switch RequestsTransport to use session in order to provide connection sharing between requests
* Added dynamic auth TTL and title functionality

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
