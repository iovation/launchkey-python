class EntityManager:
    def __init__(self, directory_manager, directory_session_manager,
                 directory_device_manager, directory_service_manager,
                 directory_service_auths_manager,
                 directory_service_policy_manager,
                 organization_service_manager,
                 organization_service_policy_manager, auth_policy_manager):
        self._directory_manager = directory_manager
        self._directory_session_manager = directory_session_manager
        self._directory_device_manager = directory_device_manager
        self._directory_service_manager = directory_service_manager
        self._directory_service_auths_manager = directory_service_auths_manager
        self._directory_service_policy_manager = \
            directory_service_policy_manager
        self._organization_service_manager = organization_service_manager
        self._organization_service_policy_manager = \
            organization_service_policy_manager
        self._auth_policy_manager = auth_policy_manager

    def get_current_auth_response(self):
        return self._directory_service_auths_manager.current_auth_request

    def get_current_directory(self):
        return self._directory_manager.current_directory

    def get_current_directory_sdk_keys(self):
        return self._directory_manager.current_sdk_keys

    def get_previous_directory_sdk_keys(self):
        return self._directory_manager.previous_sdk_keys

    def get_current_directory_list(self):
        return self._directory_manager.current_directories

    def get_current_directory_public_keys(self):
        return self._directory_manager.current_public_keys

    def get_current_directory_user_sessions(self):
        return self._directory_session_manager.current_session_list

    def get_current_user_identifier(self):
        return self._directory_device_manager.current_user_identifier

    def get_current_device(self):
        return self._directory_device_manager.current_device

    def get_current_device_list(self):
        return self._directory_device_manager.current_device_list

    def get_current_linking_response(self):
        return self._directory_device_manager.current_linking_response

    def get_current_directory_service(self):
        return self._directory_service_manager.current_service

    def get_current_directory_service_public_keys(self):
        return \
            self._directory_service_manager.current_service_public_keys

    def get_current_directory_service_list(self):
        return self._directory_service_manager.current_service_list

    def get_current_directory_service_policy(self):
        return self._directory_service_policy_manager.current_service_policy

    def set_current_directory_service_policy(self, policy):
        self._directory_service_policy_manager.current_service_policy = policy

    def get_current_organization_service(self):
        return self._organization_service_manager.current_service

    def get_current_organization_service_list(self):
        return self._organization_service_manager.current_service_list

    def get_current_organization_service_public_keys(self):
        return \
            self._organization_service_manager.current_service_public_keys

    def get_current_organization_service_policy(self):
        return self._organization_service_policy_manager.\
            current_service_policy

    def set_current_organization_service_policy(self, policy):
        self._organization_service_policy_manager.current_service_policy = \
            policy

    def get_current_auth_policy(self):
        return self._auth_policy_manager.current_policy

    def set_current_auth_policy(self, policy):
        self._auth_policy_manager.current_policy = policy
