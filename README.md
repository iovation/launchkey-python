## Python SDK for LaunchKey API 
For use in implementing LaunchKey
Version 1.0
@author LaunchKey
@created 2013-03-20
@updated 2013-06-20

#########################
## Description

Use to more easily interact with LaunchKey's API.

#########################
## Installation

    $ easy_install launchkey

#########################
## Usage

### To create a LaunchKey API object
    
    import launchkey
    #app_key will be provided in the dashboard
    app_key = 1234567890 
    #app_secret will be provided in the dashboard once, or a new one may be generated
    app_secret = "abcdefghijklmnopqrstuvwxyz123456"
    private_key = open("path/to/key.pem", "r").read()
    #Your domain, which must match in the dashboard
    domain = "http://yourdomain" 
    version = "v1"
    api = launchkey.API(app_key, app_secret, private_key, domain, "v1")


### When a user wishes to login

    auth_request = api.authorize(username)


### To check up on whether that user has launched or not

    launch_status = poll_request(auth_request)


### To figure out whether the user authorized or denied the request

    if api.is_authorized(launch_status['auth']):
    #Log username in


### When a user logs out

    api.logout(username)


#########################
## Contributing

1. Fork it
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin my-new-feature`)
5. Create new Pull Request
