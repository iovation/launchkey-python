from launchkey import LAUNCHKEY_PRODUCTION
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from .services import LaunchKeyService, DatabaseService
from .views import IndexView, AuthStatusView, DirectoryWebhookView, \
    LinkUserView, LinkView, LoginStatusView, LoginView, LogoutView, \
    UserView, ServiceWebhookView


app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile("config.py")


launchkey_service = LaunchKeyService(
    app.config['ORGANIZATION_ID'],
    app.config['ORGANIZATION_KEY'],
    app.config['DIRECTORY_ID'],
    app.config['SERVICE_ID'],
    app.config.get('LAUNCHKEY_API', LAUNCHKEY_PRODUCTION)
)

launchkey_service.update_directory_webhook_url(
    app.config['NGROK_BASE_URL'] + "/webhooks/directory"
)
launchkey_service.update_service_webhook_url(
    app.config['NGROK_BASE_URL'] + "/webhooks/service"
)


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

database_service = DatabaseService(
    db, launchkey_service, User, AuthRequest, Device)

app.add_url_rule(
    '/',
    view_func=IndexView.as_view('index_view',
                                database_service=database_service)
)
app.add_url_rule(
    '/link',
    view_func=LinkView.as_view('link_view')
)
app.add_url_rule(
    '/link-user',
    view_func=LinkUserView.as_view('link_user_view',
                                   launchkey_service=launchkey_service,
                                   database_service=database_service)
)
app.add_url_rule(
    '/login',
    view_func=LoginView.as_view('login_view',
                                launchkey_service=launchkey_service,
                                database_service=database_service)
)
app.add_url_rule(
    '/auth-status',
    view_func=AuthStatusView.as_view('auth_status_view',
                                     database_service=database_service)
)
app.add_url_rule(
    '/user',
    view_func=UserView.as_view('user_view', database_service=database_service)
)
app.add_url_rule(
    '/login-status',
    view_func=LoginStatusView.as_view('login_status_view',
                                      database_service=database_service)
)
app.add_url_rule(
    '/logout',
    view_func=LogoutView.as_view('logout_view',
                                 database_service=database_service)
)
app.add_url_rule(
    '/webhooks/service',
    view_func=ServiceWebhookView.as_view('service_webhook_view',
                                         launchkey_service=launchkey_service,
                                         database_service=database_service)
)
app.add_url_rule(
    '/webhooks/directory',
    view_func=DirectoryWebhookView.as_view('directory_webhook_view',
                                           launchkey_service=launchkey_service,
                                           database_service=database_service)
)
