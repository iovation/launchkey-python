## Python SDK for LaunchKey API  [![Build Status](https://travis-ci.org/LaunchKey/launchkey-python.png?branch=master)](https://travis-ci.org/LaunchKey/launchkey-python)
For use in implementing LaunchKey
Version 1.2.4
@author LaunchKey
@updated 2015-03-13

#########################
## Description

Use to more easily interact with LaunchKey's API.

#########################
## Installation

    $ easy_install launchkey-python
or

    $ pip launchkey-python

#########################
## Usage

### To create a LaunchKey API object

    import launchkey
    #app_key will be provided in the dashboard
    app_key = 1234567890
    #app_secret will be provided in the dashboard once, or a new one may be generated
    app_secret = "abcdefghijklmnopqrstuvwxyz123456"
    private_key = open("path/to/key.pem", "r").read()
    api = launchkey.API(app_key, app_secret, private_key)


### When a user wishes to login

    #Set session to False if it's a transactional authorization and a session doesn't need to be kept
    #If session is not specified it will automatically default to True
    session = True
    #Set user_push_id to True if you would like to be returned a value that can be used to push requests to the user in the future
    #If user_push_id is not specified it will automatically default to False
    user_push_id = False
    auth_request = api.authorize(username, session, user_push_id)


### To check up on whether that user has launched or not

    launch_status = poll_request(auth_request)


### To figure out whether the user authorized or denied the request

    if api.is_authorized(auth_request, launch_status['auth']):
        #Now log the user in


### When a user logs out

    api.logout(auth_request)

### Dealing with Callbacks (Webhooks)

Receiving an authorization

    #You will get auth_request, auth, and user_hash information in a JSON string
    auth_request = request.params['auth_request']
    auth = request.params['auth']
    user_hash = request.params['user_hash']
    #Identify the user's session by the correlating auth_request
    #Then use the is_authorized function to complete
    success = api.is_authorized(auth_request, auth)


Receiving a deorbit request

    #You will receive two parameters: deorbit and signature
    deorbit = request.params['deorbit']
    signature = request.params['signature']
    #Use the deorbit function with these parameters to get the user_hash to logout
    user_hash = api.deorbit(deorbit, signature)
    #If you've kept the auth_request stored for the correlating user_hash you can look it up
    #and use it now to log the user out
    #auth_request = get_auth_request_from_user_hash(user_hash)
    api.logout(auth_request)

### White Label

You can add users to your White Label Group via an App that belongs to the group using the new call.

    response = api.create_whitelabel_user("identifier")

It is important to note that the identifier sent in should be sent as a string and should be a non-changing value unique to that user. It is recommended to use a primary key or UUID instead of a username or email address that could be subject to change.
The response will include qrcode, code, and lk_identifier. The qrcode is a url to an image of the QR Code for the mobile application to scan. The code is a value that can be entered in the mobile application in the event the QR Code cannot be scanned. The lk_identifer is a value that should be stored for that user and used to push future authentication requests when using "authorize".


#########################
## Tests

    $ python setup.py test

#########################

## Contributing

1. Fork it
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin my-new-feature`)
5. Create new Pull Request
