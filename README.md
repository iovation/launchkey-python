## Python SDK for LaunchKey API 
For use in implementing LaunchKey  
Version 1.1.0
@author LaunchKey  
@updated 2013-09-16

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

    session = True
    #Set session to False if it's a transactional authorization and a session doesn't need to be kept.
    #If session is not specified it will automatically default to True
    auth_request = api.authorize(username, session)


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
    success = api.isauthorized(auth_request, auth)
    
    
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
    
### Extras

Optionally for additional verification you may check PINs that user devices generate. Each device a user has will have a device_id to identify it and up to 5 PIN codes which are sent in the authorization. Every time a new authorization is sent with that device to your app it will generate a new PIN code and discard the oldest. If you store the 4 newest PINs, you can match them up with each new authorization to ensure the device's authenticity.

In order to take advantage of this feature you will need to implement the following functions in your own subclass that are outlined in the SDK:

    pins_valid
    get_user_hash
    get_existing_pins
    update_pins
    

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
