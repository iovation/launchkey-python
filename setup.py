import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pycrypto',
    'requests',
    ]

setup(name='LaunchKey Python SDK',
      version='1.0',
      description='LaunchKey Python SDK',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='launchkey',
      author_email='support@launchkey.com',
      url='https://launchkey.com',
      keywords='launchkey security authentication',
      #packages=find_packages(),
      #include_package_data=True,
      #package_data={
      #  "launchkey": ["launchkey.sdk"]
      #},
      py_modules=[
          'launchkey',
      ],
      zip_safe=False,
      test_suite='tests',
      install_requires=requires,
      tests_require=[
        'Mocker',
      ],
      )
