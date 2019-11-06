from flask import session, request, render_template, redirect, abort
from flask.views import MethodView

from launchkey.entities.directory import DeviceLinkCompletionResponse
from launchkey.entities.service import AuthorizationResponse, AdvancedAuthorizationResponse, SessionEndRequest
from launchkey.exceptions import AuthorizationInProgress


class IndexView(MethodView):

    def __init__(self, database_service):
        self.database_service = database_service

    def get(self):
        if session.get('username') and self.database_service.is_user_logged_in(
                session['username']):
            return redirect("/user")
        return redirect("/login")


class LinkView(MethodView):

    @staticmethod
    def get():
        return render_template('link.html')


class LinkUserView(MethodView):

    def __init__(self, launchkey_service, database_service, logger):
        self.launchkey_service = launchkey_service
        self.database_service = database_service
        self.logger = logger

    def post(self):
        username = request.values['username']
        session['username'] = username

        linking_request = self.launchkey_service.link_device(username)
        session['device_id'] = linking_request.device_id

        self.logger.info(
            f"Link request created for user {username} "
            f"and device {linking_request.device_id}"
        )

        user = self.database_service.get_or_create_user(username)

        self.database_service.get_or_create_device(
            user.id, session['device_id'])

        return render_template('linking.html', qrcode=linking_request.qrcode,
                               code=linking_request.code)

    def get(self):
        if not session.get('device_id'):
            abort(401)
        user = self.database_service.get_or_create_user(session['username'])
        device = self.database_service.get_or_create_device(
            user.id, session['device_id'])
        status_code = 404
        if device.public_key:
            status_code = 204
        return "", status_code


class LoginView(MethodView):

    def __init__(self, launchkey_service, database_service, logger):
        self.launchkey_service = launchkey_service
        self.database_service = database_service
        self.logger = logger

    @staticmethod
    def get():
        return render_template('login-form.html')

    def post(self):
        username = request.values['username'].lower()
        session['username'] = username
        user = self.database_service.get_or_create_user(username)
        self.database_service.clear_user_session(user)

        try:
            auth_request = self.launchkey_service.authorization_request(username)
        except AuthorizationInProgress as auth_in_progress:
            self.launchkey_service.cancel_authorization_request(
                auth_in_progress.authorization_request_id
            )
            auth_request = self.launchkey_service.authorization_request(username)

        self.database_service.create_pending_auth_request(
            user.id, auth_request.auth_request)
        session['auth_request_id'] = auth_request.auth_request

        return render_template('login-status.html')


class AuthStatusView(MethodView):

    def __init__(self, database_service):
        self.database_service = database_service

    def get(self):
        if not session.get('auth_request_id'):
            abort(401)

        status_code = 404
        auth_request = self.database_service.get_auth_request(
            session['auth_request_id'])
        if auth_request.authorized:
            status_code = 204
        elif auth_request.authorized == 0:
            status_code = 403
        return "", status_code


class UserView(MethodView):

    def __init__(self, database_service):
        self.database_service = database_service

    def get(self):
        if not session.get('username'):
            abort(401)
        username = session['username']
        if not self.database_service.is_user_logged_in(username):
            return redirect("/login")
        return render_template('user.html', username=username)


class LoginStatusView(MethodView):

    def __init__(self, database_service):
        self.database_service = database_service

    def get(self):
        if not session.get('username'):
            abort(401)
        status_code = 204 if self.database_service.is_user_logged_in(
            session['username']) else 403
        return "", status_code


class LogoutView(MethodView):

    def __init__(self, database_service):
        self.database_service = database_service

    def get(self):
        if not session.get('username'):
            abort(401)
        user = self.database_service.get_or_create_user(session['username'])
        self.database_service.clear_user_session(user)
        return redirect("/login")


class ServiceWebhookView(MethodView):

    def __init__(self, launchkey_service, database_service, logger):
        self.launchkey_service = launchkey_service
        self.database_service = database_service
        self.logger = logger

    def post(self):
        package = self.launchkey_service.handle_service_webhook(
            request.data, request.headers, request.method, request.path)
        if isinstance(package, AdvancedAuthorizationResponse) or isinstance(package, AuthorizationResponse):
            self.logger.info(f"Service Webhook Received {type(package)}")
            auth_request = self.database_service.get_auth_request(
                package.authorization_request_id)
            if auth_request:
                auth_request.authorized = package.authorized
                self.database_service.db.session.add(auth_request)

                user = self.database_service.get_user_from_id(
                    auth_request.user_id)
                user.logged_in = auth_request.authorized
                user.service_user_hash = package.service_user_hash
                self.database_service.db.session.add(user)

                self.launchkey_service.session_start(
                    user.username, auth_request.id
                )

                self.database_service.db.session.commit()

                if auth_request.authorized:
                    self.logger.info(
                        f"Auth request approved and session created for "
                        f"{user.username} for auth {auth_request.id}"
                    )
                else:
                    self.logger.info(
                        f"Auth request denied for {user.username} "
                        f"for auth {auth_request.id}"
                    )
            else:
                self.logger.warn(
                    f"Auth Response WebHook received for unknown auth id "
                    f"{package.authorization_request_id}"
                )
        elif isinstance(package, SessionEndRequest):
            user = self.database_service.get_user_from_service_user_hash(
                package.service_user_hash)
            self.database_service.clear_user_session(user)
            self.logger.info(
                f"Session ended for {user.username}"
            )
        return "", 204


class DirectoryWebhookView(MethodView):

    def __init__(self, launchkey_service, database_service, logger):
        self.launchkey_service = launchkey_service
        self.database_service = database_service
        self.logger = logger

    def post(self):
        package = self.launchkey_service.handle_directory_webhook(
            request.data, request.headers, request.method, request.path)
        if isinstance(package, DeviceLinkCompletionResponse):
            self.logger.info(f"Device link request received:\n"
                             f"device id: {package.device_id}\n"
                             f"public key id: {package.device_public_key_id}\n"
                             f"public key: {package.device_public_key}")
            device = self.database_service.get_device(package.device_id)
            if device:
                device.public_key = package.device_public_key
                device.public_key_id = package.device_public_key_id
                self.database_service.db.session.add(device)
                self.database_service.db.session.commit()
            else:
                self.logger.warn(
                    f"Device Link Completion WebHook received for unknown "
                    f"device id {package.device_id}"
                )
        return "", 204
