LaunchKey Webhooks Example App
==============================

Example webapp to demonstrate LaunchKey webhooks using 
the Python Service SDK and Flask.

For more information on LaunchKey webhooks see:

https://docs.launchkey.com/api/webhooks/index.html


Installation
------------

Install ngrok: https://ngrok.com/

Install Pipenv: https://docs.pipenv.org/en/latest/


.. code-block:: bash
    
    $ pipenv install

Usage
-----


.. code-block:: bash
    
    $ ngrok http 5000
    $ cp instance/example_config.py instance/config.py
    $ # Update config.py to include the returned ngrok url and your LaunchKey credentials
    $ pipenv shell
    $ FLASK_APP=launchkey_example_app flask run
