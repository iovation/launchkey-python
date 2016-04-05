Python SDK for LaunchKey API 
For use in implementing LaunchKey
Version 1.0
@author LaunchKey
@created 2013-03-20
@updated 2013-05-01

#########################
Description
-------------------------

Use to more easily interact with LaunchKey's API.

#########################


#########################
Usage
-------------------------

'''To create a LaunchKey API object'''
import launchkey
#app_key will be provided in the dashboard
app_key = 12345667890 
#app_secret will be provided in the dashboard once, or a new one may be generated
app_secret = "abcdefghijklmnopqrstuvwxyzabcdef"
private_key = open("path/to/key", "r").read()
#Domain as specified in the dashboard
domain = "http://yourdomain" 
version = "v1"
api = launchkey.API(app_key, app_secret, private_key, domain, "v1")

'''When a user wishes to login'''
auth_request = api.authorize(username)

'''To check up on whether that user has launched or not'''
launch_status = poll_request(auth_request)

'''To figure out whether the user authorized or denied the request'''
if api.is_authorized(launch_status['auth']):
	#Log username in

'''When a user logs out'''
api.logout(username)

#########################