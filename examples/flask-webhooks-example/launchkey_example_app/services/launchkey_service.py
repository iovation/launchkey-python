from launchkey.factories import OrganizationFactory


class LaunchKeyService:
    def __init__(self, organization_id, organization_key, directory_id,
                 service_id, launchkey_url, use_advanced_webhooks):
        self.organization_id = organization_id
        self.directory_id = directory_id
        self.service_id = service_id

        organization_factory = OrganizationFactory(
            organization_id,
            organization_key,
            url=launchkey_url
        )
        self.organization_client = organization_factory.\
            make_organization_client()
        self.directory_client = organization_factory.make_directory_client(
            directory_id
        )
        self.service_client = organization_factory.make_service_client(
            service_id
        )

        self.use_advanced_webhooks = use_advanced_webhooks

    def update_directory_webhook_url(self, webhook_url):
        self.organization_client.update_directory(
            self.directory_id,
            webhook_url=webhook_url
        )

    def update_service_webhook_url(self, webhook_url):
        self.directory_client.update_service(
            self.service_id,
            callback_url=webhook_url
        )

    def link_device(self, username):
        return self.directory_client.link_device(username)

    def authorization_request(self, username):
        return self.service_client.authorization_request(username)

    def cancel_authorization_request(self, auth_request_id):
        self.service_client.cancel_authorization_request(
            auth_request_id
        )

    def session_start(self, username, auth_request_id):
        self.service_client.session_start(
            username, auth_request_id
        )

    def session_end(self, username):
        self.service_client.session_end(username)

    def handle_service_webhook(self, body, headers, method, path):
        if self.use_advanced_webhooks:
            return self.service_client.handle_advanced_webhook(body, headers, method, path)
        else:
            return self.service_client.handle_webhook(body, headers, method, path)

    def handle_directory_webhook(self, body, headers, method, path):
        return self.directory_client.handle_webhook(body, headers, method, path)
