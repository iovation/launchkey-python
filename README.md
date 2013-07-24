## Python SDK for LaunchKey API 
For use in implementing LaunchKey  
Version 1.0.3  
@author LaunchKey  
@created 2013-03-20  
@updated 2013-07-24

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
    auth_request = api.authorize(username, session)


### To check up on whether that user has launched or not

    launch_status = poll_request(auth_request)


### To figure out whether the user authorized or denied the request

    if api.is_authorized(auth_request, launch_status['auth']):
        #Log the user in


### When a user logs out

    api.logout(auth_request)

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
