import requests
from time import sleep


class Version:
    def __init__(self, id, state=None, version=None, native_properties=None, latest=None):
        """
        Kobiton App Version.

        Note that no values are required based on the spec so any value can
        default to None.

        See: See: https://api.kobiton.com/docs/#app
        :param id:
        :param state:
        :param version:
        :param native_properties:
        :param latest:
        """
        self.id = id
        self.state = state
        self.version = version
        self.native_properties = native_properties
        self.latest = latest


class App:
    def __init__(self, id, name=None, state=None, created_at=None, private_access=None, os=None, created_by=None,
                 bypass=None, organization_id=None, icon_url=None, versions=None):
        """
        Kobiton app

        Note that no values are required based on the spec so any value can
        default to None.

        See: https://api.kobiton.com/docs/#app
        :param id:
        :param name:
        :param state:
        :param created_at:
        :param private_access:
        :param os:
        :param created_by:
        :param bypass:
        :param organization_id:
        :param icon_url:
        :param versions:
        """
        self.id = id
        self.name = name
        self.state = state
        self.created_at = created_at
        self.private_access = private_access
        self.os = os
        self.created_by = created_by
        self.bypass = bypass
        self.organization_id = organization_id
        self.icon_url = icon_url
        self.versions = versions

    def __repr__(self):
        return "App <id={id}, name=\"{name}\", state=\"{state}\">".format(
            id=self.id,
            name=self.name,
            state=self.state
        )


class Device:
    def __init__(self, id, udid, is_booked, is_hidden, is_online, model_name, device_name,
                 resolution, platform_name, platform_version, installed_browsers, support,
                 device_image_url, is_favorite, is_cloud, is_my_org, is_my_own, hosted_by):
        """
        Kobition device

        Note that no values are required based on the spec so any value can
        default to None.

        See: https://api.kobiton.com/docs/#clouddevice
        :param id:
        :param udid:
        :param is_booked:
        :param is_hidden:
        :param is_online:
        :param model_name:
        :param device_name:
        :param resolution:
        :param platform_name:
        :param platform_version:
        :param installed_browsers:
        :param support:
        :param device_image_url:
        :param is_favorite:
        :param is_cloud:
        :param is_my_org:
        :param is_my_own:
        :param hosted_by:
        """
        self.id = id
        self.udid = udid
        self.is_booked = is_booked
        self.is_hidden = is_hidden
        self.is_online = is_online
        self.model_name = model_name
        self.device_name = device_name
        self.resolution = resolution
        self.platform_name = platform_name
        self.platform_version = platform_version
        self.installed_browser = installed_browsers
        self.support = support
        self.device_image_url = device_image_url
        self.is_favorite = is_favorite
        self.is_cloud = is_cloud
        self.is_my_org = is_my_org
        self.is_my_own = is_my_own
        self.hosted_by = hosted_by

    def __repr__(self):
        return "Device <{device_name}>".format(device_name=self.device_name)


class KobitonManager:
    def __init__(self, username, sdk_key, url='https://api.kobiton.com', api_version='v1'):
        """
        Manager for interacting with Kobiton
        :param username: Kobition username
        :param sdk_key: Kobiton sdk key associated with the given username
        :param url: Kobiton API url
        :param api_version: Kobiton API version
        """
        self.__username = username
        self.__sdk_key = sdk_key
        self.__url = url
        self.__api_version = api_version

    def _create_request(self, method, endpoint, json=None, data=None,
                        params=None):
        """
        Creates an request to the Kobition API
        :param method: HTTP method to use
        :param endpoint: API endpoint to query IE: devices, sessions, user, app
        :param json: Optional. JSON body data to include.
        :param data: Optional. Dictionary, list of tuples, bytes, or file-like
        object to send in the body.
        :param params: Optional. GET parameters to include.
        :return: Dictionary containing response data or boolean stating success
        status if no data was returned.
        """
        response = getattr(requests, method.lower())(
            self.__url + "/" + self.__api_version + "/" + endpoint,
            headers={
                'Accept': 'application/json'
            },
            auth=(self.__username, self.__sdk_key),
            data=data,
            json=json,
            params=params
        )
        response.raise_for_status()
        return response.json() if response.text != "OK" else response.ok

    def _generate_upload_url(self, filename):
        """
        Generates an upload URL
        https://api.kobiton.com/docs/#generate-upload-url
        :param filename:
        :return: Dictionary containing appPath and url (S3 bucket url).
        """
        return self._create_request('post', 'apps/uploadUrl/', json={
            "filename": filename
        })

    def _create_app(self, app_name, app_path):
        """
        Creates an application to be accessed by Kobiton devices
        https://api.kobiton.com/docs/#create-application-or-version
        :param app_name: Designated app filename IE: my_app.apk
        :param app_path: App path returned by the _generate_upload_url()
        :return: Dictionary containing filename and appId keys
        """
        return self._create_request('post', 'apps', json={
            "filename": app_name,
            "appPath": app_path
        })

    def _upload_app_to_s3(self, app_path, s3_url):
        """
        Uploads a given app to a S3 url
        :param app_path: Filepath to the app to be uploaded.
        :param s3_url: S3 URL to upload to. This url should have been returned
        by _generate_upload_url().
        :return: None
        """
        with open(app_path, 'rb') as f:
            data = f.read()
            response = requests.put(
                s3_url,
                data=data,
                headers={
                    'Content-Type': 'application/octet-stream',
                    'x-amz-tagging': 'unsaved=true'
                }
            )
            response.raise_for_status()

    def get_apps(self):
        """
        Get list of applications which were added to the Apps Repo.
        https://api.kobiton.com/docs/#get-applications
        :return: List of kobiton_manager.App objects.
        """
        return [
            App(
                app['id'],
                app['name'],
                app['state'],
                created_at=app.get('createdAt'),
                private_access=app.get('privateAccess'),
                os=app.get('os'),
                created_by=app.get('createdBy'),
                bypass=app.get('bypass'),
                organization_id=app.get('organizationId'),
                icon_url=app.get('iconUrl'),
                versions=[
                    Version(
                        version['id'],
                        version['state'],
                        version['version'],
                        version['nativeProperties'],
                        version.get('latest')
                    ) for version in app.get('versions', [])
                ]
            ) for app in self._create_request('get', 'apps').get('apps', [])
        ]

    def get_app(self, app_id):
        """
        Get information about an application.
        https://api.kobiton.com/docs/#get-an-application
        :param app_id: The ID to the app
        :return: kobiton_manager.App object
        """
        app = self._create_request('get', 'apps/%s' % app_id)
        return App(
            app['id'],
            app['name'],
            app['state'],
            created_at=app.get('createdAt'),
            private_access=app.get('privateAccess'),
            os=app.get('os'),
            created_by=app.get('createdBy'),
            bypass=app.get('bypass'),
            organization_id=app.get('organizationId'),
            icon_url=app.get('iconUrl'),
            versions=[
                Version(
                    version['id'],
                    version['state'],
                    version['version'],
                    version['nativeProperties'],
                    version.get('latest')
                ) for version in app.get('versions', [])
            ]
        )

    def upload_app(self, app_path, app_name=None, retrieve_app_status=False):
        """
        Uploads an application via Kobiton's application upload flow:
        https://docs.kobiton.com/basic/app-repository/integrate-apps-repo-with-ci/
        :param app_path: Filepath to the app to be uploaded.
        :param app_name: Optional. App name to label the uploaded app as.
        :param retrieve_app_status: Whether to pull the full app information
        after upload. If not, an app with only id and the uploaded version id
        will be returned.
        :return: kobiton_manager.App object
        """
        app_name = app_name if app_name else app_path.split("/")[-1]
        upload_data = self._generate_upload_url(app_name)
        self._upload_app_to_s3(app_path, upload_data['url'])
        app = self._create_app(app_name, upload_data['appPath'])
        if retrieve_app_status:
            try:
                app = self.get_app(app['appId'])
            except requests.HTTPError:
                # We seem to be getting a 500 if we query
                # immediately after creating the app
                sleep(2)
                app = self.get_app(app['appId'])
        else:
            app = App(app['appId'], versions=[Version(app['versionId'])])

        return app

    def delete_app(self, app_id):
        """
        Deletes a given APP ID from Kobiton
        :param app_id:
        :return:
        """
        return self._create_request('delete', 'apps/%s' % app_id)

    def get_devices(self):
        """
        Retrieves a list of Kobiton devices
        :return: List of kobiton_manager.Device objects
        """
        response = self._create_request(
            'get',
            'devices'
        )

        return [
            Device(
                device.get('id'),
                device.get('udid'),
                device.get('isBooked'),
                device.get('isHidden'),
                device.get('isOnline'),
                device.get('modelName'),
                device.get('deviceName'),
                device.get('resolution'),
                device.get('platformName'),
                device.get('platformVersion'),
                device.get('installedBrowsers'),
                device.get('support'),
                device.get('deviceImageUrl'),
                device.get('isFavorite'),
                device.get('isCloud'),
                device.get('isMyOrg'),
                device.get('isMyOwn'),
                device.get('hostedBy')
            ) for device in response['cloudDevices']
        ]
