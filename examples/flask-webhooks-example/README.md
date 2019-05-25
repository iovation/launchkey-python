Python SDK for LaunchKey API
============================

.. _LaunchKey: https://launchkey.com

Example webapp to demonstrate LaunchKey_ using the Python Service SDK.

Examples
--------

CLI Example
***********

`Go to the README <examples/cli/README.md>`_

Installation
------------


.. code-block:: bash

    $ pipenv install

Usage
-----

.. code-block:: bash
    
    $ ngrok http 5000
    $ cp example_config.py config.py
    $ # Update config.py to include your cred and the ngrok url confirmed
    $ FLASK_APP=app.py flask run
