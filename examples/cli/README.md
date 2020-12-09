# TruValidate Multifactor Authentication Python SDK CLI


  * [Installation](#installation)
  * [Usage](#usage)
    * [Help](#help)
    * [Commands](#commands)
    * [Service User Session Management](#service)
    * [Directory User Device Management](#directory)
    * [TOTP](#totp)

## <a name="installation"></a>Installation

Ensure you have pipenv installed:

https://pipenv.readthedocs.io/en/latest/
 
Then install the requirements and set up the virtual environment:

```bash
pipenv install
```

## <a name="usage"></a>Usage

The CLI is ran through the cli.py script:

First enter the virtual environment that was installed above:

```bash
pipenv shell
```

Then:

```bash
python cli.py [OPTIONS]
```

### <a name="help"></a>Help
  
Help can be obtained by either executing the application without any parameters or with --help.

```
python cli.py --help
```

### <a name="commands"></a>Commands

There are two sections of commands which have a number of actions they can perform.

  * [Service User Session Management](#service)
    * authorize
    * cancel-auth-request
    * session-start
    * session-end
  * [Directory User Device Management](#directory)
    * device-link
    * devices-list
    * device-unlink

### <a name="service"></a>Service User Session Management

The example CLI provides the ability to manage a user session for an Service. Services are managed utilizing
Service credentials for the Service ID you provide in the calls.

  1. Login
  
        Performing an authorization request is accomplished with the authorize action which is passed a username.

        Example: Execute an authorization request for an Organization _bdc16040-976e-11e7-bb33-5e1e4c59c6c8_ with a private key _/tmp/private.key_ user _MyUsername_, the service ID of 
        _cc07872d-1f99-41e4-8359-eaff0d2269d9_.

        ```
        python cli.py organization bdc16040-976e-11e7-bb33-5e1e4c59c6c8 /tmp/private.key authorize cc07872d-1f99-41e4-8359-eaff0d2269d9 MyUsername
        ```
        
        Optional arguments include: 
        ```
        python cli.py organization bdc16040-976e-11e7-bb33-5e1e4c59c6c8 /tmp/private.key authorize cc07872d-1f99-41e4-8359-eaff0d2269d9 MyUsername --context "My Context" --title "My Title" --ttl 60 --push-title "Push Title" --push-body "Push Body"
        ```

        The request will happen in two steps.  The service will make an authorization request and then poll for a user
        response:  That portion will look something like this:

        ```
        Authorization request successful
            Auth Request: 03b99174-c23d-4bff-ae50-d56de719d4d4
        Checking for response from user.
        ..............
        ```

        One of three scenarios will occur.  The request will timeout or the user will accept or reject the request.  Here are
        examples of each:

        Request timed out:

        ```
        Authorization request timed out.
        ```
        
        Request canceled:

        ```
        Authorization request canceled.
        ```

        User accepted:

        ```
        Authorization request accepted by user.
            Resp Type:     AUTHORIZED
            Resp Reason:   APPROVED
            Denial Reason: None
            Is Fraud:      False
            Auth Request:  03b99174-c23d-4bff-ae50-d56de719d4d4
            Device ID:     b0daea36-2994-11e9-8dac-0242ac130009
            Svc User Hash: B8luyaSwKdFnABYghEZdPLb3QI7RJ02yfYnAr67EPpi
            User Push ID:  eff2bb17-86e4-4a4b-8b0d-2e46b5d8609b
            Org User Hash: imEYzSoMIe1KBcInb1RnkL2qXvuG7NKeoFvzkX0fOS4
        ```

        User rejected:

        ```
        Authorization request rejected by user.
            Resp Type:      DENIED
            Resp Reason:    FRAUDULENT
            Denial Reason:  den12
            Is Fraud:       True
            Auth Request:   03b99174-c23d-4bff-ae50-d56de719d4d4
            Device ID:      b0daea36-2994-11e9-8dac-0242ac130009
            Svc User Hash:  B8luyaSwKdFnABYghEZdPLb3QI7RJ02yfYnAr67EPpi
            User Push ID:   eff2bb17-86e4-4a4b-8b0d-2e46b5d8609b
            Org User Hash:  imEYzSoMIe1KBcInb1RnkL2qXvuG7NKeoFvzkX0fOS4
        ```
    
  2. Cancel an authorization request
        
        Authorization requests can be canceled if they have not expired or been responded to.

        Example: Cancel an authorization request for an Organization _bdc16040-976e-11e7-bb33-5e1e4c59c6c8_ with a private key _/tmp/private.key_ user _MyUsername_, the service ID of 
        _cc07872d-1f99-41e4-8359-eaff0d2269d9_ and auth request id of _03b99174-c23d-4bff-ae50-d56de719d4d4_.
        
        ```
        python cli.py organization bdc16040-976e-11e7-bb33-5e1e4c59c6c8 /tmp/private.key cancel-auth-request cc07872d-1f99-41e4-8359-eaff0d2269d9 03b99174-c23d-4bff-ae50-d56de719d4d4
        ```

        Would result in one of the following scenarios:
        
        Success: 

        ```
        Authorization request canceled.
        ```
        
        Canceling an auth that has been responded to:
        
        ```
        Authorization request has already been responded to.
        ```
        
        Canceling an already canceled auth:
         
        ```
        Authorization request already canceled.
        ```

        Using an auth id that belongs to another Service or has expired:

        ```
        Authorization request not found.
        ```

  3. Start a user session 

        Pass the Username to the session-start action

        ```
        python cli.py organization bdc16040-976e-11e7-bb33-5e1e4c59c6c8 /tmp/private.key session-start cc07872d-1f99-41e4-8359-eaff0d2269d9 MyUsername
        ```

        You will receive the message:

        ```
        User session is started.
        ```

  4. End a user session
  
        Pass the Username to the session-end action

        ```
        python cli.py organization bdc16040-976e-11e7-bb33-5e1e4c59c6c8 /tmp/private.key session-end cc07872d-1f99-41e4-8359-eaff0d2269d9 MyUsername
        ```

        You will receive the message:

        ```
        User session is ended.
        ```

### <a name="directory"></a>Directory User Device Management

Directory User devices are authenticators utilizing the Authenticator SDK.  The linking and unlinking of devices for 
users in your application can be achieved via "directory" commands.

Directory commands are performed utilizing credentials for the Directory.

  1. Linking a Device

        Pass a unique identifier for the end user in your system to the device-link action. The example request below is
        for an Organization _bdc16040-976e-11e7-bb33-5e1e4c59c6c8_ with a private key _/tmp/private.key_ a directory id of
        _3cb7c699-be47-414f-830b-e81b9bb8cc40_ and a user identifier of _326335b0-8569-4aa3-90a3-ac4372104ea3_.

        Request:
    
        ```
        python cli.py organization bdc16040-976e-11e7-bb33-5e1e4c59c6c8 /tmp/private.key device-link 3cb7c699-be47-414f-830b-e81b9bb8cc40 326335b0-8569-4aa3-90a3-ac4372104ea3

        ```

        Response when Directory User is successfully created:

        ```
        Device link request successful
            QR Code URL: https://api.launchkey.com/public/v3/qr/5r53j9z
            Manual verification code: 5r53j9z
        ```
    
  2. Listing the Devices linked to a Directory User

        Pass a unique identifier for a user in your system to the devices-list action. The example request below is
        for an Organization bdc16040-976e-11e7-bb33-5e1e4c59c6c8 with a private key _/tmp/private.key_ a directory id of
        3cb7c699-be47-414f-830b-e81b9bb8cc40 and a user identifier of 326335b0-8569-4aa3-90a3-ac4372104ea3.

        Request:

        ```
        python cli.py organization bdc16040-976e-11e7-bb33-5e1e4c59c6c8 /tmp/private.key devices-list 3cb7c699-be47-414f-830b-e81b9bb8cc40 326335b0-8569-4aa3-90a3-ac4372104ea3
        ```

        Response when no devices were found:

        ```
        No devices found for the given identifier.
        ```

        Response when devices are found

        ```
        device:
            ID:      c932b32a-e6eb-11e8-9146-b60ebeaffa0f
            Type:    iOS
            Status:  LINKED
        
        device2:
            ID:      5bce8c75-6d77-46a2-9d88-17543803fd89
            Type:    Android
            Status:  LINKED
        ```
  
  3. Unlinking a Device

        Pass a unique identifier for the end user in your system to the device-unlink action. The example request below is
        for an Organization _bdc16040-976e-11e7-bb33-5e1e4c59c6c8_ with a private key _/tmp/private.key_ a directory id of
        _3cb7c699-be47-414f-830b-e81b9bb8cc40_, a user identifier of _326335b0-8569-4aa3-90a3-ac4372104ea3_, and a device
        identifier of _c932b32a-e6eb-11e8-9146-b60ebeaffa0f_.

        Request:
    
        ```
        python cli.py organization bdc16040-976e-11e7-bb33-5e1e4c59c6c8 /tmp/private.key devices-unlink 3cb7c699-be47-414f-830b-e81b9bb8cc40 326335b0-8569-4aa3-90a3-ac4372104ea3 c932b32a-e6eb-11e8-9146-b60ebeaffa0f

        ```

        Response when Device is successfully unlinked:

        ```
        Device unlinked
        ```
### <a name="totp"></a>TOTP

TOTP can be configured, removed, and verified for a Directory User.

Directory commands are performed utilizing credentials for the Directory.

  1. Configuring TOTP for a Directory User
  
        Pass a unique identifier for the end user in your system to the `generate-user-totp` action. The example request below is
        for an Organization _bdc16040-976e-11e7-bb33-5e1e4c59c6c8_ with a private key _/tmp/private.key_ a directory id of
        _3cb7c699-be47-414f-830b-e81b9bb8cc40_, and a user identifier of _326335b0-8569-4aa3-90a3-ac4372104ea3_.

        Request:
    
        ```
        python cli.py organization bdc16040-976e-11e7-bb33-5e1e4c59c6c8 /tmp/private.key generate-user-totp 3cb7c699-be47-414f-830b-e81b9bb8cc40 326335b0-8569-4aa3-90a3-ac4372104ea3

        ```

        Response when a user successfully has TOTP configured:

        ```
        TOTP Generated for User
        Algorithm:  SHA1
        Digits: 6
        Period: 30
        Secret: 6FNFGYQLLWVMPNTGGUWC7XFVA2WU5FKU
        
        █▀▀▀▀▀█ ▄█▄▄▀███▀ ▄▀  ██▄▀▄▀█▄▄▀█▀▄█  █▀▄ ▀▀ ▀█▄ █ ██ █▀▀▀▀▀█
        █ ███ █ ▄ █▄██ █▀  ██▀█ ▄█ ▄▄███ ██ █▄█ ▄  █▀ █ ▀▀█▀█ █ ███ █
        █ ▀▀▀ █ ▀▄▀▄▄▀▄▄▄█▄ ▄█▄▀█▄███▀▀▀██▄▄▀ ▀ ██▄██▀ ▀ ██▀  █ ▀▀▀ █
        ▀▀▀▀▀▀▀ █ ▀ █ █▄█▄▀ █ █▄▀ █ █ ▀ █▄█▄█ ▀ █▄█▄█▄█ ▀▄█ ▀ ▀▀▀▀▀▀▀
         ▀▄▀█▀▀ █▀█  █▀   ▀█▀▄█  ▄▄ ▀▀▀▀▀█▄████ █▄█▄  █▀▀█▄ ▄██▄█▀ ▀
        ▄█   █▀▀▄▀██▄▄▀██▀▀▀ ▀█▀███▀▄▄▄▀▀▄▄██ ▀█  ▄▀▄ █▄█▄▀▀   ███▄ █
         ▀ ▀▀█▀█▀▀▄▀▄ ▄▄ █▄█▄█ ▀▀█▄▄▄█▄█▄▀   ▄█▀▀██ █   ▄█▀▄▀ ▄▀▀█▀▄▀
        █ ▀▄ ▀▀▄▀▄▀ █   █ █▀▄ ███ █▄▄█▀███▄▀  ▄▀▀ ██▀ ▄███ ▀█▄▀▄ ▀▄▄▀
        ▄▀▄██ ▀ ▄▀  ██▄ ▄▄██▄ ▄ ▀▀▄ ▀  █▄▄ ███▀ ▄▄▄▄▀█▀▄▄██▄██▀ ██▀▀▀
          ▄█▀▄▀▀▄ █▄██  ▄▄ ▀ ▄ ▄▄▀   █▄▄▀▀   ▄   █▄▀█▄▄█▀█ ▄▀█ █▀█▀█▀
        █▀█▄ ▀▀▀▄ ▀▄ ▄ █▄▄ ▀▀█ ██▄    ▄█ ▀ ▀▀▀█  █▄ ▄▀█▄█▀▀█▄ ▀█▄█  █
        █▀█ █ ▀▄█▀ ▄▄ ▀ ▀   ▄▄█ ▀  ▀▀  ▀██▄█ ▀  ▀▀▄▄████▀▄▀▄▄█▄▄▄█▄▄█
        █▀ ▄ ▄▀█▀█▄▀█  ▀ ▀▄██▀▄ ▀█▀ ▄█▀▄  ▀▄█▄█▀ █  ▀▀ ██▀█▀ ██▄█▀▄█▄
        █▀▀█▀▀▀█▀▀▄▄ ██▀▀█ ▀ ▀ ▀▀▄▀▄ ▀█▄█▀▀█ ▄▀ ▄▄▀ ▀██▄ ██▄▀▄▄  ▄▄▀█
        █▀███▀▀▀█▄█▀▄█ ▀ ▄▄▀██▄ ▄▄▄▄█▀▀▀█ █▄▀▀▀▀▀▀▄█ ▄▄ ▀▄▀▀█▀▀▀█▀███
        ▀██▄█ ▀ █▀ ▄▄▄█  █ ▄▄  █ █▄▄█ ▀ █▀  ▀▄▄  █▀█ █▄▀▀▀▄ █ ▀ █  ▄▄
        ▀ █ █▀▀███  █ ▀█ ▄▀▄▄▄█▀▄ ▀█▀▀█▀█▄▀██▀▀▄ ▄▄█▄▄▄ ▀ ▄▄▀████▄▄▀
        ▀▀█▀ █▀▀▀▀▀█▀█▀█▀▀▄  ██▄ ██▀  ▄▀▄▀█  █▄▄ █ ▀▄▄██ █ █▄▀▀▀█▀▄██
        ██▄█▄▀▀▄█▀   ▀▄█▀▄ █▀███▄██▀   ▀█▄▄▀▀▄▀ ▀▀▄▄▄ ▀ ▀▀█▀▄▀███  █▄
         ▄ ▄▀█▀▄██ █▀ █▀▀█▀▀██▀ ▄▄ ▀▀ ▄█▀▀█ ▀██▄▀ █ ▀▄▄▀ ▀█▄▄ ▀█▀▄▄▀█
        █  █▄ ▀▄█▀▄    ▄▀█▄▄ █▀▄▀ █▄ ▄█ ▀█▄▄▀▀▄█▄██▀ █▄▀ ▄▀▀██▀██▄█▄
         ▀█▄█ ▀█  ▀███ ▄▄▄ ▀▄▄  ▀▀▄▀▄█▄▀ █ ▄▄▀ █ █ ▄▀█▄ ████ █▀█▄  ▄▀
        █ ▄▄ ▄▀ ▄█▄ ▄ ▀█ ▀█▀▄█ ▀ ▄█ ▀██▄█▀█▄██▀ ██▄ ▄▄▄  ▀▄▀ ▀███▄█ ▀
        ▀██▄▄▀▀ █ █▀▄█  ▄▄█▀▄▄█▀ ███▄█ ▄█▄▀██▄▀ ▄ ▀▀█▀█▄▀▄█▄█▀▀  █  █
        ▄▀▀▀ █▀▄▀▄ ▄█  ▄▄▀█▄▄▀▄█ ▀▄   ██▄ ▀█▄ █▄█ █ █▀▄▄▀█▀█▀▄ ▄▄███▀
        ▄▄█▀█▀▀█▀▀▀▀▄█ ▄▄▀▄█▄▄▀▀█ ▄▀▄ ▄▀ ▄   ▀█ ▄▀ █ ▄▀▀▀█ █  █ █ █ ▀
        ▀▀▀▀  ▀ █ ██▄▀█▀ ▀ ▄▄██▄ █▄▀█▀▀▀█▀ ▀ ▀ ▀▄ █ █   █ ███▀▀▀██ ▄▀
        █▀▀▀▀▀█ ▄ █ ▄█▄   ▀▄▄▄ ▀ ▄█▀█ ▀ ██  ▀▄▄▀█▄▄█▀█▀▄▀█ ▀█ ▀ █▄ ▄▀
        █ ███ █ █▀  ▀█▄█  █▄ ▄▄▄█ ▀▄█▀▀▀▀▄▄▄  █▀ ▄▀ ▄█▀ ▀▀▄▀▀█▀▀▀▄▄ █
        █ ▀▀▀ █ ▄ ▀█▄▀██▀ ▀█▀ ▄ ▀ ▀█▄ ██▄█ █ ▄  ▀▀▀▀▀▀  ▀█ █ ▀▄█▀▄▄██
        ▀▀▀▀▀▀▀  ▀ ▀ ▀▀ ▀▀  ▀▀  ▀ ▀▀▀ ▀▀▀  ▀▀▀ ▀▀ ▀▀ ▀  ▀ ▀  ▀▀ ▀   ▀
        ```
  
  2. Removing TOTP for a user
  
        Pass a unique identifier for the end user in your system to the `remove-user-totp` action. The example request below is
        for an Organization _bdc16040-976e-11e7-bb33-5e1e4c59c6c8_ with a private key _/tmp/private.key_ a directory id of
        _3cb7c699-be47-414f-830b-e81b9bb8cc40_, and a user identifier of _326335b0-8569-4aa3-90a3-ac4372104ea3_.
        
        Request:
    
        ```
        python cli.py organization bdc16040-976e-11e7-bb33-5e1e4c59c6c8 /tmp/private.key remove-user-totp 3cb7c699-be47-414f-830b-e81b9bb8cc40 326335b0-8569-4aa3-90a3-ac4372104ea3

        ```

        Response when a user successfully has TOTP removed:

        ```
        TOTP configuration removed from user
        ```
  
  3. Verifying a One Time Password
        
        Pass a unique identifier for the end user in your system and the otp code to the `verify-user-totp` action. The example request below is
        for an Organization _bdc16040-976e-11e7-bb33-5e1e4c59c6c8_ with a private key _/tmp/private.key_ a service id of
        _998a8274-e261-11ea-a66b-da5a0a740c04_, and a user identifier of _326335b0-8569-4aa3-90a3-ac4372104ea3_.
        
        Request:
    
        ```
        python cli.py organization bdc16040-976e-11e7-bb33-5e1e4c59c6c8 /tmp/private.key verify-user-totp 998a8274-e261-11ea-a66b-da5a0a740c04 326335b0-8569-4aa3-90a3-ac4372104ea3 123456

        ```

        Response when a TOTP code is valid:

        ```
        Input OTP code was valid
        ```
        
        Response when a TOTP code is invalid:
        ```
        Input OTP code was not valid
        ```
  
        