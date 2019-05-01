from launchkey.factories import OrganizationFactory
from launchkey import LAUNCHKEY_PRODUCTION

from steps.managers import DirectoryManager, DirectoryDeviceManager, \
    DirectoryServiceManager, DirectoryServiceAuthsManager, \
    DirectoryServicePolicyManager, DirectoryServiceSessionManager, \
    DirectorySessionManager, KeysManager, OrganizationServiceManager, \
    OrganizationServicePolicyManager, EntityManager, AuthPolicyManager, \
    SampleAppDeviceManager, AppiumDeviceManager, KobitonManager


def before_all(context):
    context.organization_factory = OrganizationFactory(
        context.organization_id,
        context.organization_private_key,
        url=getattr(context, 'launchkey_url', LAUNCHKEY_PRODUCTION)
    )
    sample_app_package = 'com.launchkey.android.authenticator.demo'

    desired_caps = dict()
    # Increase the default idle time in order to prevent the session from
    # closing while non device tests are being ran.
    desired_caps['newCommandTimeout'] = 300
    desired_caps['appPackage'] = sample_app_package
    desired_caps[
        'appWaitActivity'] = 'com.launchkey.android.authenticator.demo.' \
                             'ui.activity.ListDemoActivity'
    desired_caps['fullReset'] = True
    desired_caps['noReset'] = False
    desired_caps['captureScreenshots'] = True
    desired_caps['disableWindowAnimation'] = True

    if hasattr(context, 'appium_url'):
        desired_caps['platformName'] = context.platform_name
        desired_caps['platformVersion'] = context.platform_version
        desired_caps['automationName'] = 'UiAutomator2'
        desired_caps['deviceName'] = context.device_name
        desired_caps['app'] = context.sample_app_apk_path
        context.appium_device_manager = AppiumDeviceManager(
            context.appium_url,
            desired_caps,
            sample_app_package,
            timeout_period=10
        )
    elif hasattr(context, 'kobiton_username') and hasattr(context,
                                                          'kobiton_sdk_key'):
        context.kobiton_manager = KobitonManager(context.kobiton_username,
                                                 context.kobiton_sdk_key)
        context.uploaded_app = context.kobiton_manager.upload_app(
            context.sample_app_apk_path)

        devices = context.kobiton_manager.get_devices()
        for device in devices:
            # Look for a device that is not currently booked (check out by
            # another user), is online and ready to use, is Android (currently
            # the only supported device type), and a platform that is greater
            # than 5.0
            if not device.is_booked and device.is_online and device.platform_name == "Android" and \
                    int(device.platform_version[0]) > 5:
                desired_caps['platformName'] = device.platform_name
                desired_caps['platformVersion'] = device.platform_version
                desired_caps['automationName'] = 'UiAutomator2'
                desired_caps['deviceName'] = device.device_name
                desired_caps['app'] = "kobiton-store:v%s" % \
                                      context.uploaded_app.versions[0].id

                context.appium_device_manager = AppiumDeviceManager(
                    'https://%s:%s@api.kobiton.com/wd/hub' % (
                        context.kobiton_username, context.kobiton_sdk_key),
                    desired_caps,
                    sample_app_package,
                    timeout_period=10
                )
                break
        if 'deviceName' not in desired_caps:
            raise Exception(
                "No viable device found in Kobiton. Note that you need "
                "an available Android device with an OS > v5.0.0")

    if hasattr(context, 'appium_device_manager'):
        context.sample_app_device_manager = SampleAppDeviceManager(
            context.appium_device_manager
        )


def after_all(context):
    if hasattr(context, 'appium_device_manager'):
        context.appium_device_manager.quit()
    if hasattr(context, 'uploaded_app'):
        context.kobiton_manager.delete_app(context.uploaded_app.id)


def before_feature(context, feature):
    pass


def after_feature(context, feature):
    pass


def before_scenario(context, scenario):

    if 'device_testing' in scenario.effective_tags:
        if hasattr(context, 'appium_device_manager'):
            # Reset the app each time a new device scenario begins
            context.appium_device_manager.reset()
        else:
            # Skip device scenarios when the tester has not added
            # configurations for them
            scenario.skip("Missing Appium configurations")

    context.directory_manager = DirectoryManager(context.organization_factory)
    context.directory_device_manager = DirectoryDeviceManager(
        context.organization_factory)
    context.directory_service_manager = DirectoryServiceManager(
        context.organization_factory)
    context.directory_service_auths_manager = DirectoryServiceAuthsManager(
        context.organization_factory)
    context.directory_service_policy_manager = DirectoryServicePolicyManager(
        context.organization_factory)
    context.directory_service_session_manager = DirectoryServiceSessionManager(
        context.organization_factory)
    context.directory_session_manager = DirectorySessionManager(
        context.organization_factory)
    context.keys_manager = KeysManager()
    context.organization_service_manager = OrganizationServiceManager(
        context.organization_factory)
    context.organization_service_policy_manager = OrganizationServicePolicyManager(
        context.organization_factory)
    context.auth_policy_manager = AuthPolicyManager()
    context.entity_manager = EntityManager(
        context.directory_manager,
        context.directory_session_manager,
        context.directory_device_manager,
        context.directory_service_manager,
        context.directory_service_auths_manager,
        context.directory_service_policy_manager,
        context.organization_service_manager,
        context.organization_service_policy_manager,
        context.auth_policy_manager
    )
    context.current_exception = None


def after_scenario(context, scenario):
    context.directory_device_manager.cleanup()
