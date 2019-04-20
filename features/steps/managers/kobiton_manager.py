import requests
from time import sleep


class Version:
    def __init__(self, id, state=None, version=None, native_properties=None, latest=None):
        self.id = id
        self.state = state
        self.version = version
        self.native_properties = native_properties
        self.latest = latest


class App:
    def __init__(self, id, name=None, state=None, created_at=None, private_access=None, os=None, created_by=None,
                 bypass=None, organization_id=None, icon_url=None, versions=None):
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
        self.__username = username
        self.__sdk_key = sdk_key
        self.__url = url
        self.__api_version = api_version

    def _create_request(self, method, endpoint, json=None, data=None, params=None):
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
        return self._create_request('post', 'apps/uploadUrl/', json={
            "filename": filename
        })

    def _create_app(self, app_name, app_path):
        return self._create_request('post', 'apps', json={
            "filename": app_name,
            "appPath": app_path
        })

    def _upload_app_to_s3(self, app_path, s3_url):
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
        return self._create_request('delete', 'apps/%s' % app_id)

    def get_devices(self, is_booked=False):
        response = self._create_request(
            'get',
            'devices',
            params={
                'isBooked': is_booked
            }
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
