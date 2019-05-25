from launchkey import LAUNCHKEY_PRODUCTION
from launchkey.factories import OrganizationFactory
from launchkey.entities.directory import DeviceLinkCompletionResponse
from launchkey.entities.service import AuthorizationResponse, SessionEndRequest
from launchkey.exceptions import AuthorizationInProgress
from flask import Flask, request, render_template, session, abort, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_pyfile("config.py")
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    current_pending_auth = db.Column(db.String, unique=True)
    service_user_hash = db.Column(db.String, unique=True)
    logged_in = db.Column(db.Integer)

    def __repr__(self):
        return '<User %r>' % self.username


class AuthRequest(db.Model):
    id = db.Column(db.String, primary_key=True)
    user_id = db.Column(db.Integer)
    authorized = db.Column(db.Integer)

    def __repr__(self):
        return '<AuthRequest %r>' % self.id


class Device(db.Model):
    id = db.Column(db.String, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    public_key_id = db.Column(db.String)
    public_key = db.Column(db.String)

    def __repr__(self):
        return '<Device %r>' % self.id


db.drop_all()
db.create_all()


organization_factory = OrganizationFactory(
    app.config['ORGANIZATION_ID'],
    app.config['ORGANIZATION_KEY'],
    url=app.config.get('LAUNCHKEY_API', LAUNCHKEY_PRODUCTION)
)
organization_client = organization_factory.make_organization_client()
organization_client.update_directory(
    app.config['DIRECTORY_ID'],
    webhook_url=app.config['NGROK_BASE_URL'] + "/webhooks/directory"
)
directory_client = organization_factory.make_directory_client(
    app.config['DIRECTORY_ID']
)
directory_client.update_service(
    app.config['SERVICE_ID'],
    callback_url=app.config['NGROK_BASE_URL'] + "/webhooks/service"
)

service_client = organization_factory.make_service_client(
    app.config['SERVICE_ID']
)


def is_user_logged_in(username):
    user = get_or_create_user(username)
    return user.logged_in if user else False


def get_or_create_user(username):
    username = username.lower()
    user = User.query.filter_by(username=username).first()
    if not user:
        user = User(
            username=username
        )
        db.session.add(user)
        db.session.commit()
    return user


def get_user_from_service_user_hash(user_hash):
    return User.query.filter_by(service_user_hash=user_hash).first()


def get_user_from_id(user_id):
    return User.query.filter_by(id=user_id).first()


def clear_user_session(user):
    auth_request = get_auth_request(user.current_pending_auth)
    user.current_pending_auth = None
    user.logged_in = False
    db.session.add(user)
    if auth_request:
        db.session.delete(auth_request)
    db.session.commit()
    service_client.session_end(user.username)


def get_device(device_id):
    return Device.query.filter_by(id=device_id).first()


def get_user_devices(username):
    user = get_or_create_user(username)
    return Device.query.filter_by(user_id=user.id).all()


def create_pending_auth_request(user_id, auth_request_id):
    auth = AuthRequest(id=auth_request_id, user_id=user_id)
    db.session.add(auth)
    db.session.commit()


def get_auth_request(auth_request_id):
    return AuthRequest.query.filter_by(id=auth_request_id).first()


def get_or_create_device(user_id, device_id):
    device_id = device_id
    device = get_device(device_id)
    if not device:
        device = Device(
            id=device_id,
            user_id=user_id
        )
        db.session.add(device)
        db.session.commit()
    return device


@app.route("/")
def index():
    if session.get('username') and is_user_logged_in(session['username']):
        return redirect("/user")
    return redirect("/login")


@app.route("/link")
def link():
    return render_template('link.html')


@app.route("/link-user", methods=["POST"])
def link_user_post():
    username = request.values['username']
    session['username'] = username

    linking_request = directory_client.link_device(username)
    session['device_id'] = linking_request.device_id

    user = get_or_create_user(username)

    get_or_create_device(user.id, session['device_id'])

    return render_template('linking.html', qrcode=linking_request.qrcode,
                           code=linking_request.code)


@app.route("/link-user", methods=["GET"])
def link_user_get():
    if not session.get('device_id'):
        abort(401)
    user = get_or_create_user(session['username'])
    device = get_or_create_device(user.id, session['device_id'])
    status_code = 404
    if device.public_key:
        status_code = 204
    return "", status_code


@app.route("/login", methods=["GET"])
def login_get():
    return render_template('login-form.html')


@app.route("/login", methods=["POST"])
def login_post():
    username = request.values['username'].lower()
    session['username'] = username
    user = get_or_create_user(username)
    clear_user_session(user)

    try:
        auth_request = service_client.authorization_request(username)
    except AuthorizationInProgress as auth_in_progress:
        service_client.cancel_authorization_request(
            auth_in_progress.authorization_request_id
        )
        auth_request = service_client.authorization_request(username)

    create_pending_auth_request(user.id, auth_request.auth_request)
    session['auth_request_id'] = auth_request.auth_request

    return render_template('login-status.html')


@app.route("/auth-status", methods=["GET"])
def auth_status_get():
    if not session.get('auth_request_id'):
        abort(401)

    status_code = 404
    auth_request = get_auth_request(session['auth_request_id'])
    if auth_request.authorized:
        status_code = 204
    elif auth_request.authorized == 0:
        status_code = 403
    return "", status_code


@app.route("/user", methods=["GET"])
def user_get():
    if not session.get('username'):
        abort(401)
    username = session['username']
    if not is_user_logged_in(username):
        return redirect("/login")
    devices = get_user_devices(username)
    app.logger.info(devices)
    return render_template('user.html', username=username, devices=devices)


@app.route("/login-status", methods=["GET"])
def login_status_get():
    if not session.get('username'):
        abort(401)
    status_code = 204 if is_user_logged_in(session['username']) else 403
    return "", status_code


@app.route("/logout", methods=["GET"])
def logout():
    if not session.get('username'):
        abort(401)
    user = get_or_create_user(session['username'])
    clear_user_session(user)
    return redirect("/login")


@app.route("/webhooks/service", methods=["POST"])
def service_webhook():
    package = service_client.handle_webhook(request.data, request.headers,
                                              request.method, request.path)
    if isinstance(package, AuthorizationResponse):
        app.logger.info("Auth Response Received")
        auth_request = get_auth_request(package.authorization_request_id)
        app.logger.info(f"Auth Request: {auth_request}")
        if auth_request:
            app.logger.info(f"Authorized: {package.authorized}")
            auth_request.authorized = package.authorized
            db.session.add(auth_request)

            user = get_user_from_id(auth_request.user_id)
            user.logged_in = auth_request.authorized
            user.service_user_hash = package.service_user_hash
            db.session.add(user)

            service_client.session_start(
                user.username, auth_request.id
            )

            db.session.commit()
    elif isinstance(package, SessionEndRequest):
        app.logger.info("Session End Request Received")
        user = get_user_from_service_user_hash(package.service_user_hash)
        clear_user_session(user)
    return "", 204


@app.route("/webhooks/directory", methods=["POST"])
def directory_webhook():
    package = directory_client.handle_webhook(request.data, request.headers,
                                              request.method, request.path)
    if isinstance(package, DeviceLinkCompletionResponse):
        device = get_device(package.device_id)
        if device:
            device.public_key = package.device_public_key
            device.public_key_id = package.device_public_key_id
            db.session.add(device)
            db.session.commit()
    return "", 204
