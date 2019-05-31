class DatabaseService:

    def __init__(self, db, launchkey_service, user_model, auth_request_model,
                 device_model):
        self.db = db
        self.launchkey_service = launchkey_service
        self.user_model = user_model
        self.auth_request_model = auth_request_model
        self.device_model = device_model

    def is_user_logged_in(self, username):
        user = self.get_or_create_user(username)
        return user.logged_in if user else False

    def get_or_create_user(self, username):
        username = username.lower()
        user = self.user_model.query.filter_by(username=username).first()
        if not user:
            user = self.user_model(
                username=username
            )
            self.db.session.add(user)
            self.db.session.commit()
        return user

    def get_user_from_service_user_hash(self, user_hash):
        return self.user_model.query.filter_by(
            service_user_hash=user_hash).first()

    def get_user_from_id(self, user_id):
        return self.user_model.query.filter_by(id=user_id).first()

    def clear_user_session(self, user):
        auth_request = self.get_auth_request(user.current_pending_auth)
        user.current_pending_auth = None
        user.logged_in = False
        self.db.session.add(user)
        if auth_request:
            self.db.session.delete(auth_request)
        self.db.session.commit()
        self.launchkey_service.session_end(user.username)

    def get_device(self, device_id):
        return self.device_model.query.filter_by(id=device_id).first()

    def get_user_devices(self, username):
        user = self.get_or_create_user(username)
        return self.device_model.query.filter_by(user_id=user.id).all()

    def create_pending_auth_request(self, user_id, auth_request_id):
        auth = self.auth_request_model(id=auth_request_id, user_id=user_id)
        self.db.session.add(auth)
        self.db.session.commit()

    def get_auth_request(self, auth_request_id):
        return self.auth_request_model.query.filter_by(
            id=auth_request_id).first()

    def get_or_create_device(self, user_id, device_id):
        device_id = device_id
        device = self.get_device(device_id)
        if not device:
            device = self.device_model(
                id=device_id,
                user_id=user_id
            )
            self.db.session.add(device)
            self.db.session.commit()
        return device
