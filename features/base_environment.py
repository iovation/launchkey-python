from launchkey.factories import OrganizationFactory
from launchkey import LAUNCHKEY_PRODUCTION

from steps.managers import DirectoryManager, DirectoryDeviceManager, \
    DirectoryServiceManager, DirectoryServiceAuthsManager, \
    DirectoryServicePolicyManager, DirectoryServiceSessionManager, \
    DirectorySessionManager, KeysManager, OrganizationServiceManager, \
    OrganizationServicePolicyManager, EntityManager, AuthPolicyManager


def before_all(context):
    context.organization_factory = OrganizationFactory(
        context.organization_id,
        context.organization_private_key,
        url=getattr(context, 'launchkey_url', LAUNCHKEY_PRODUCTION)
    )


def after_all(context):
    pass


def before_feature(context, feature):
    pass


def after_feature(context, feature):
    pass


def before_scenario(context, scenario):
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
