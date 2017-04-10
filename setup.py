import os
from setuptools import setup
from launchkey import SDK_VERSION

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()

requires = [
    'requests >= 2.5.1', 'requests < 3.0.0',
    'six >= 1.10.0', 'six < 2.0.0',
    'pycrypto >= 2.6.1', 'pycrypto < 3.0.0',
    'python-dateutil >= 2.4.2', 'python-dateutil < 3.0.0',
    'formencode >= 1.3.1', 'formencode < 2.0.0',
    'pyjwkest >= 1.3.2', 'pyjwkest < 2.0.0'
    ]

setup(name='launchkey',
      version=SDK_VERSION,
      description='LaunchKey Python SDK',
      long_description=README + '\n\n' + CHANGES + '\n',
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='iovation',
      url='https://www.iovation.com/',
      keywords='launchkey security authentication iovation multifactor mfa 2fa biometric',
      license='MIT',
      py_modules=[
          'launchkey',
      ],
      packages=[
          'launchkey',
          'launchkey.clients',
          'launchkey.exceptions',
          'launchkey.factories',
          'launchkey.transports'
      ],
      zip_safe=False,
      test_suite='tests',
      install_requires=requires,
      tests_require=[
        'nose >= 1.3.0', 'nose < 2.0.0',
        'nose-exclude >= 0.5.0', 'nose-exclude < 1.0.0',
        'mock >= 2.0.0', 'mock < 3.0.0'
      ],
      )
