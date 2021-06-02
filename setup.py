import os
from setuptools import setup
from launchkey import SDK_VERSION

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()

requires = [
    'setuptools >= 40.4.3',
    'requests >= 2.5.1, < 3.0.0',
    'six >= 1.10.0, < 2.0.0',
    'python-dateutil >= 2.4.2, < 3.0.0',
    'formencode >= 1.3.1, < 2.0.0',
    'pyjwkest >= 1.3.2, < 2.0.0',
    'pycryptodomex >= 3.4.12, < 4.0.0',
    'enum34 >= 1.1.6, < 2.0.0; python_version < "3.4"',
    'urllib3 >=1.26.5, < 2.0.0',
    'pytz'
]

setup(name='launchkey',
      version=SDK_VERSION,
      description='LaunchKey Python SDK',
      long_description=README + '\n\n' + CHANGES + '\n',
      long_description_content_type="text/x-rst",
      classifiers=[
          "Programming Language :: Python",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
          "Topic :: System :: Systems Administration :: Authentication/Directory",
          "Programming Language :: Python :: Implementation :: CPython",
          "Programming Language :: Python :: Implementation :: PyPy",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.5",
          "Programming Language :: Python :: 3.6",
          "Programming Language :: Python :: 3.7",
          "Natural Language :: English",
          "Intended Audience :: Developers",
      ],
      author='iovation',
      url='https://github.com/iovation/launchkey-python',
      keywords='launchkey security authentication iovation multifactor mfa 2fa biometric',
      license='MIT',
      py_modules=[
          'launchkey',
      ],
      packages=[
          'launchkey',
          'launchkey.clients',
          'launchkey.entities',
          'launchkey.entities.service',
          'launchkey.exceptions',
          'launchkey.factories',
          'launchkey.transports',
          'launchkey.utils'
      ],
      zip_safe=False,
      test_suite='tests',
      install_requires=requires,
      tests_require=[
          'nose >= 1.3.0, < 2.0.0',
          'nose-exclude >= 0.5.0, < 1.0.0',
          'mock >= 2.0.0, < 3.0.0',
          'ddt >= 1.1.1, < 2.0.0'
      ],
      project_urls={
          'Bug Reports': 'https://github.com/iovation/launchkey-python/issues',
          'Documentation': 'https://docs.launchkey.com/service-sdk/python/sdk-v3/',
          'Administration': 'https://admin.launchkey.com/',
      },
      )
