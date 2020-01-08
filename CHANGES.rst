CHANGELOG for LaunchKey Python SDK
==================================

3.7.0
-----

* Add device ID list to `AuthorizationRequest` object
* Update CLI to display device ID list upon authorization request

3.6.0
-----

* Bug fix to ensure that requests do not follow redirects
* Bug fix to ensure that public key is cached using `kid` header of JWT found within a response header
* Added Policies: ConditionalGeofence, MethodAmount, Factors, Legacy
* Added Requirement enum
* enum34 only required on python versions < 3.4
* Deprecated: TimeFence
* Deprecated: `ServiceSecurityPolicy`
* Deprecated: `get_service_policy` method on `ServiceManagingBaseClient` class
* Deprecated: `set_service_policy` method on `ServiceManagingBaseClient` class
* Deprecated: `get_authorization_response` method on `ServiceClient` class
* Deprecated: `handle_webhook` method on `ServiceClient` class
* Added: `get_advanced_service_policy` method on `ServiceManagingBaseClient` class
* Added: `set_advanced_service_policy` method on `ServiceManagingBaseClient` class
* Added: `get_advanced_authorization_response` method on `ServiceClient` class
* Added: `handle_advanced_webhook` method on `ServiceClient` class
* Added: `AdvancedAuthorizationResponse` class
* Added: `AuthorizationResponsePolicy` class

3.5.0
-----

* Added get_all_directory_sdk_keys method to Organization client
* Added integration testing suite
* Added device failure sensor type
* Added auth_methods and auth_policy attributes to the AuthorizationResponse object
* Added handle_webhook as well as DeviceLinkCompletionResponse into the DirectoryClient
* Updated the OrganizationClient update_directory() method and Directory object to include a webhook_url kwarg / attribute
* Added Webhook example app

3.4.0
-----

* Added example CLI to codebase
* Added ttl parameter to the DirectoryClient link_device method
* Added cancel_authorization_request method to the ServiceClient
* Fixed bug in ServiceClient which prevented handling of session end webhook request data when presented as a bytearray

3.3.1
-----

* Updated HTTP transport to no longer use sessions due to a bug that was causing BadStatusLine exceptions on long lived connections.

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
