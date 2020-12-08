import random
import string

import click
import qrcode

from launchkey.factories import OrganizationFactory, DirectoryFactory, \
    ServiceFactory
from launchkey.exceptions import AuthorizationInProgress, \
    AuthorizationRequestCanceled, AuthorizationResponseExists, \
    EntityNotFound, RequestTimedOut
from launchkey.entities.service import DenialReason

from helpers import wait_for_response, get_service_client, \
    get_directory_client, print_result, SUCCESS_COLOR, \
    FAILURE_COLOR


@click.group()
@click.argument("entity_type", type=click.STRING)
@click.argument("entity_id", type=click.UUID)
@click.argument("private_key", type=click.File('rb'))
@click.option('--api', '-u', default="https://api.launchkey.com",
              help="API URL to send auth requests. Defaults to "
                   "https://api.launchkey.com",
              type=click.STRING)
@click.option('--encryption-key', '-e',
              help="Path to encryption key file if separate encryption and "
                   "signature keys are desired. The initially given key will "
                   "be used as a signature key.",
              type=click.File('rb'))
@click.pass_context
def main(ctx, entity_type, entity_id, private_key, api, encryption_key):
    """
    ENTITY_TYPE: Entity type for the given ID. This can be a Service,
    Directory, or Organization.

    ENTITY_ID: Entity ID in the form of a UUID for the given Service,
    Directory, or Organization.

    PRIVATE_KEY: Path to private key belonging to the given entity ID.
    If an encryption key is also given via --encryption-key, this key will
    be the signature key.
    IE: /path/to/my.key
    """

    # ensure that ctx.obj exists and is a dict (in case `cli()` is called
    # by means other than the `if` block below
    ctx.ensure_object(dict)

    entity_type = entity_type.lower()
    private_key = private_key.read()
    if entity_type == "organization":
        ctx.obj['factory'] = OrganizationFactory(entity_id, private_key,
                                                 url=api)
    elif entity_type == "directory":
        ctx.obj['factory'] = DirectoryFactory(entity_id, private_key, url=api)
    elif entity_type == "service":
        ctx.obj['factory'] = ServiceFactory(entity_id, private_key, url=api)
    else:
        raise TypeError("Input entity type is not valid. Should be one of: "
                        "Organization, Directory, Service.")

    if encryption_key:
        ctx.obj['factory'].add_additional_private_key(encryption_key.read())


@main.command()
@click.argument("service_id", type=click.STRING)
@click.argument("username", type=click.STRING)
@click.option('--context',
              help="Auth context to pair with the auth and "
                   "display to the user.",
              type=click.STRING)
@click.option('--title',
              help="Auth title to display in the auth request window.",
              type=click.STRING)
@click.option('--ttl',
              help="How long the auth request should remain active for "
                   "until it expires.",
              type=click.INT)
@click.option('--push-title',
              help="Title to appear in the push message. "
                   "This will not work for Organization Services or when "
                   "using 3rd party push.",
              type=click.STRING)
@click.option('--push-body',
              help="Body to appear in the push message. "
                   "This will not work for Organization Services or when "
                   "using 3rd party push.",
              type=click.STRING)
@click.option('--denial-reason-count',
              help="How many custom denial reasons to include. "
                   "If this is not included default denial reasons are used.",
              type=click.IntRange(min=2))
@click.option('--use-advanced',
              is_flag=True,
              default=False,
              help="Whether to retrieve the Advanced Authorization Response "
                   "or the old Authorization Response",
              type=click.BOOL)
@click.pass_context
def authorize(ctx, service_id, username, context, title, ttl, push_title,
              push_body, denial_reason_count, use_advanced):
    """SERVICE_ID USERNAME"""
    client = get_service_client(service_id, ctx.obj['factory'])

    try:

        denial_reasons = None
        if denial_reason_count:
            denial_reasons = []
            for x in range(0, denial_reason_count):
                fraud = \
                    bool(random.randint(0, 1)) if x not in (0, 1) else bool(x)
                denial_reasons.append(
                    DenialReason(
                        denial_id=str(x),
                        reason="{0}-{1}-{2}".format(
                            "f" if fraud else "nf",
                            x,
                            ''.join(
                                random.choice(
                                    string.ascii_uppercase +
                                    string.ascii_lowercase +
                                    string.digits + " "*10
                                ) for _ in range(random.randint(5, 70))
                            )
                        ),
                        fraud=fraud
                    )
                )

        auth = client.authorization_request(
            username,
            context=context,
            title=title,
            ttl=ttl,
            push_title=push_title,
            push_body=push_body,
            denial_reasons=denial_reasons
        )
        print_result(
            "Authorization request successful",
            {
                "Auth Request": auth.auth_request,
                "Push Package": auth.push_package,
                "Device IDs": auth.device_ids
            },
            color=SUCCESS_COLOR
        )
    except AuthorizationInProgress as pre_existing_auth:
        print_result(
            pre_existing_auth.message,
            {
                "Auth Request": pre_existing_auth.authorization_request_id,
                "Expires": pre_existing_auth.expires,
                "Same Service": pre_existing_auth.from_same_service
            },
            color=FAILURE_COLOR
        )
        return

    click.echo("Checking for response from user.")

    try:
        if use_advanced:
            auth_response = wait_for_response(
                client.get_advanced_authorization_response, [auth.auth_request]
            )
        else:
            auth_response = wait_for_response(
                client.get_authorization_response, [auth.auth_request]
            )

        if auth_response.authorized:
            message = "Authorization request approved by user."
            color = SUCCESS_COLOR
        else:
            message = "Authorization request rejected by user."
            color = FAILURE_COLOR

        print_result(
            message,
            {
                "Resp Type":
                    auth_response.type.value if auth_response.type else None,
                "Resp Reason":
                    auth_response.reason.value if auth_response.reason
                    else None,
                "Denial Reason": auth_response.denial_reason,
                "Is Fraud": auth_response.fraud,
                "Auth Request": auth_response.authorization_request_id,
                "Device ID": auth_response.device_id,
                "Svc User Hash": auth_response.service_user_hash,
                "User Push ID": auth_response.user_push_id,
                "Org User Hash": auth_response.organization_user_hash,
                "Auth Methods": auth_response.auth_methods,
                "Auth Policy": auth_response.policy if use_advanced else
                auth_response.auth_policy
            },
            color=color
        )
    except RequestTimedOut:
        click.secho(
            "\nAuthorization request timed out.",
            fg=FAILURE_COLOR
        )
    except AuthorizationRequestCanceled:
        click.secho(
            "\nAuthorization request canceled.",
            fg=FAILURE_COLOR
        )


@main.command()
@click.argument("service_id", type=click.STRING)
@click.argument("auth_id", type=click.STRING)
@click.pass_context
def cancel_auth_request(ctx, service_id, auth_id):
    """SERVICE_ID AUTH_ID"""
    client = get_service_client(service_id, ctx.obj['factory'])
    try:
        client.cancel_authorization_request(auth_id)
        click.secho(
            "Authorization request canceled.", fg=SUCCESS_COLOR
        )
    except AuthorizationRequestCanceled:
        click.secho(
            "Authorization request already canceled.", fg=FAILURE_COLOR
        )
    except AuthorizationResponseExists:
        click.secho(
            "Authorization request has already been responded to.",
            fg=FAILURE_COLOR
        )
    except EntityNotFound:
        click.secho(
            "Authorization request not found.", fg=FAILURE_COLOR
        )


@main.command()
@click.argument("service_id", type=click.STRING)
@click.argument("username", type=click.STRING)
@click.pass_context
def session_start(ctx, service_id, username):
    """SERVICE_ID USERNAME"""
    client = get_service_client(service_id, ctx.obj['factory'])
    client.session_start(username, None)
    click.secho("User session is started.", fg=SUCCESS_COLOR)


@main.command()
@click.argument("service_id", type=click.STRING)
@click.argument("username", type=click.STRING)
@click.pass_context
def session_end(ctx, service_id, username):
    """SERVICE_ID USERNAME"""
    client = get_service_client(service_id, ctx.obj['factory'])
    client.session_end(username)
    click.secho("User session is ended.", fg=SUCCESS_COLOR)


@main.command()
@click.argument("directory_id", type=click.STRING)
@click.argument("user_identifier", type=click.STRING)
@click.option(
    '--ttl',
    help="How long the linking / QR code should remain active "
         "for until they expire.",
    type=click.INT
)
@click.pass_context
def device_link(ctx, directory_id, user_identifier, ttl):
    """DIRECTORY_ID USER_IDENTIFIER"""
    client = get_directory_client(directory_id, ctx.obj['factory'])
    kwargs = {}
    if ttl is not None:
        kwargs['ttl'] = ttl
    link_response = client.link_device(user_identifier, **kwargs)
    print_result(
        "Device link request successful",
        {
            "QR Code URL": link_response.qrcode,
            "Linking code": link_response.code,
            "Device ID": link_response.device_id
        },
        color=SUCCESS_COLOR
    )


@main.command()
@click.argument("directory_id", type=click.STRING)
@click.argument("user_identifier", type=click.STRING)
@click.pass_context
def devices_list(ctx, directory_id, user_identifier):
    """DIRECTORY_ID USER_IDENTIFIER"""
    client = get_directory_client(directory_id, ctx.obj['factory'])
    devices = client.get_linked_devices(user_identifier)
    if devices:
        for device in devices:
            print_result(
                device.name if device.name else "Pending Device",
                {
                    "ID": device.id,
                    "Type": device.type if device.type else "N/A",
                    "Status": device.status.status_code
                }
            )
    else:
        click.secho(
            "No devices found for the given identifier.",
            fg=FAILURE_COLOR
        )


@main.command()
@click.argument("directory_id", type=click.STRING)
@click.argument("user_identifier", type=click.STRING)
@click.argument("device_identifier", type=click.STRING)
@click.pass_context
def device_unlink(ctx, directory_id, user_identifier, device_identifier):
    """DIRECTORY_ID USER_IDENTIFIER DEVICE_IDENTIFIER"""
    client = get_directory_client(directory_id, ctx.obj['factory'])
    client.unlink_device(user_identifier, device_identifier)
    click.secho("Device unlinked", fg=SUCCESS_COLOR)


@main.command()
@click.argument("directory_id", type=click.STRING)
@click.argument("user_identifier", type=click.STRING)
@click.pass_context
def generate_user_totp(ctx, directory_id, user_identifier):
    """DIRECTORY_ID USER_IDENTIFIER"""
    client = get_directory_client(directory_id, ctx.obj['factory'])
    response = client.generate_user_totp(user_identifier)
    print_result(
        "TOTP Generated for User",
        {
            "Algorithm": response.algorithm,
            "Digits": response.digits,
            "Period": response.period,
            "Secret": response.secret
        },
        color=SUCCESS_COLOR
    )

    provisioning_uri = \
        f"otpauth://totp/LaunchKey%20Test%20TOTP:{user_identifier}?" \
            f"digits={response.digits}" \
            f"&secret={response.secret}" \
            f"&algorithm={response.algorithm}" \
            f"&period={response.period}" \
            f"&issuer=LaunchKey+Test+TOTP"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_Q,
        box_size=10,
        border=4,
    )
    qr.add_data(provisioning_uri)
    qr.make(fit=True)
    qr.print_ascii()


@main.command()
@click.argument("directory_id", type=click.STRING)
@click.argument("user_identifier", type=click.STRING)
@click.pass_context
def remove_user_totp(ctx, directory_id, user_identifier):
    """DIRECTORY_ID USER_IDENTIFIER"""
    client = get_directory_client(directory_id, ctx.obj['factory'])
    client.remove_user_totp(user_identifier)
    click.secho("TOTP configuration removed from user", fg=SUCCESS_COLOR)


@main.command()
@click.argument("service_id", type=click.STRING)
@click.argument("user_identifier", type=click.STRING)
@click.argument("otp_code", type=click.STRING)
@click.pass_context
def verify_user_totp(ctx, service_id, user_identifier, otp_code):
    """SERVICE_ID USER_IDENTIFIER OTP_CODE"""
    client = get_service_client(service_id, ctx.obj['factory'])
    valid = client.verify_totp(user_identifier, otp_code)
    if valid is True:
        click.secho("Input OTP code was valid", fg=SUCCESS_COLOR)
    else:
        click.secho("Input OTP code was not valid", fg=FAILURE_COLOR)


if __name__ == "__main__":
    main(obj={})
