Python SDK for LaunchKey API
============================

.. image:: https://travis-ci.org/iovation/launchkey-python.svg?branch=master
    :target: https://travis-ci.org/iovation/launchkey-python

.. _LaunchKey: https://launchkey.com

For use in implementing LaunchKey_.


Description
-----------

Use to more easily interact with iovation's LaunchKey API.

Installation
------------


.. code-block:: bash

    $ easy_install launchkey

or

.. code-block:: bash

    $ pip install launchkey

Usage
-----

Using LaunchKey Clients
***********************

The LaunchKey SDK is broken into credential based factories with access to functionality based clients.

**Factories**

Factories are based on the credentials supplied. The Organization Factory uses Organization credentials, the Directory
Factory uses Directory credentials, and the Service Factory uses Service credentials. Each factory provides clients
which are accessible to the factory. The availability is based on the hierarchy of the entities themselves. Below is a
matrix of available services for each factory.

+--------------+------------------+----------------+
| Factory      | Directory Client | Service Client |
+==============+==================+================+
| Organization |       Yes        |      Yes       |
+--------------+------------------+----------------+
| Directory    |       Yes        |      Yes       |
+--------------+------------------+----------------+
| Service      |       No         |      Yes       |
+--------------+------------------+----------------+

**Using individual clients**

.. code-block:: python

    from launchkey.factories import ServiceFactory, DirectoryFactory

    directory_id = "37d98bb9-ac71-44b7-9ac0-5d75e31e627a"
    directory_private_key = open('directory_private_key.key').read()
    service_id = "9ecc57e0-fb0f-4971-ba12-399b630158b0"
    service_private_key = open('service_private_key.key').read()

    directory_factory = DirectoryFactory(directory_id, directory_private_key)
    directory_client = directory_factory.make_directory_client()

    service_factory = ServiceFactory(service_id, service_private_key)
    service_client = service_factory.make_service_client()

**Using a hierarchical client**

.. code-block:: python

    from launchkey.factories import OrganizationFactory

    organization_id = "bff1602d-a7b3-4dbe-875e-218c197e9ea6"
    organization_private_key = open('organization_private_key.key').read()
    directory_id = "37d98bb9-ac71-44b7-9ac0-5d75e31e627a"
    service_id = "9ecc57e0-fb0f-4971-ba12-399b630158b0"
    user = "my_unique_internal_identifier"

    organization_factory = OrganizationFactory(organization_id, organization_private_key)
    directory_client = organization_factory.make_directory_client(directory_id)
    service_client = organization_factory.make_service_client(service_id)

Linking And Managing Users
**************************

In order to link a user you will need to start the linking process then display the qrcode to them, give them the code,
or both.

.. code-block:: python

    link_data = directory_client.link_device(user)
    linking_code = link_data.code
    qr_url = link_data.qrcode

If desired you can retrieve the user's devices and unlink then directly from the SDK

.. code-block:: python

    devices = directory_client.get_linked_devices(user)
    directory_client.unlink_device(user, devices[0].id)

You can also end all of a user's sessions

.. code-block:: python

    directory_client.end_all_service_sessions(user)

Logging A User In
*****************

Create an auth request to initiated the login process

.. code-block:: python

    auth_request_id = service_client.authorize(user)

Using Dynamic Policies

.. code-block:: python

    from launchkey.clients.service import AuthPolicy
    # Require 2 factors and don't allow any jailbroken or rooted devices
    policy = AuthPolicy(any=2, jailbreak_protection=True)
    # Also make it so the user can only log in from the Portland area
    policy.add_geofence(latitude=45.48805749706375, longitude=-122.70492553710936, radius=27500)
    auth_request_id = service_client.authorize(user, policy=policy)


Check whether a response has been received and check whether it has been authorized

.. code-block:: python

    from launchkey.exceptions import RequestTimedOut
    from time import sleep
    response = None
    try:
        while response is None:
            response = service_client.get_authorization_response(auth_request_id)
            if response is not None:
                if response.authorized is True:
                    # User accepted the auth, now create a session
                    service_client.session_start(user, auth_request_id)
                else:
                    # User denied the auth request
            else:
                sleep(1)
    except RequestTimedOut:
        # The user did not respond to the request in the timeout period (5 minutes)

When a user logs out

.. code-block:: python

    service_client.session_end(user)

Dealing with Webhooks
*********************

Webhooks can be used in opposition to polling. This means we will hit your app on either an auth response or
logout request.

You will use the same handle_webhook method for both login and logout.

**Note that request.headers must be a dictionary like object.**

.. code-block:: python

    from flask import request
    from launchkey.clients.service import AuthorizationResponse, SessionEndRequest
    package = service_client.handle_webhook(request.data, request.headers)
    if isinstance(package, AuthorizationResponse):
        if package.authorized is True:
            # User accepted the auth, now create a session
            service_client.session_start(user, auth_request_id)
        else:
            # User denied the auth
    elif isinstance(package, SessionEndRequest):
        # The package will have the user hash, so use it to log the user out based on however you are handling it
        logout_user_from_my_app(package.service_user_hash)


Running Tests
-------------

Mac/Linux:

    python setup.py test

Windows:

    setup.py test

Contributing
------------

1. Fork it
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin my-new-feature`)
5. Create new Pull Request
