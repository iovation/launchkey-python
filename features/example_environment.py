from base_environment import before_all as base_before_all, \
    after_all as base_after_all, \
    before_scenario as base_before_scenario, \
    after_scenario as base_after_scenario, \
    before_feature as base_before_feature, \
    after_feature as base_after_feature


def before_all(context):
    context.organization_id = "00d744c9-f407-4139-aff2-2713ce91532f"
    context.organization_private_key = """-----BEGIN RSA PRIVATE KEY-----
MIIEogIBAAKCAQEA3Hr+tUtwauvZ2+awUKwdBc88PQCcLM4zutkJwy0sWPxHbG9b
pqovpcFVly1kToJaCLqzwfNUrvHuMR9w81RZKIhNQ0+sBf71/FigvfMYTuHV0qcS
mdg2suS3JOxr8txpuptrwRSN7zc/LA2lNLg1cGgQjiZSJdshl9ehxPW6vNRHIStd
YRSwCPFer+gh1j1sVWsWi0Sq2jKDrkFV86vLEADEDXrekZUJzdt/eC4PlQ4GrZDl
crQZe53ubwRyHr0s/D3K+n7b1PNGZBMT1ivL1mh1Uehp07O7kvBvnY4BI0lP8zax
0Auy2byY7t7C36qUPR7k2l/sfUCRefQj2pOBPwIDAQABAoIBAC4/cnwu5dbXwCwb
WLKjV7cnQDh/j0LqwfkYm66gJCRKTuUU+sGcA0CerEh40giR2TbpitlNJF9KCi+t
q7Cu6cDRznsnFCtxzsFvCdCuVFP/lS2JtCInM1oVFcGeAgrAZ0EoZtLqb9dU3GBu
QFAtr6/zdD2NFkAwlfxW0+0Pqmr/LHyDeS1BHsxTCXhjt0JLyTT8EhTVN63O42BW
wtfOO2AZujaxrJNDokMTdONCZpbxkQvyQsgymVbTOIuEwrwsEsInriyBMegWHCdt
t5WtcQNl+KGZTSklJOkuHXZZrgosXOI3yzQe5oCIWJJ+EC+pjeTy3kV2d3pjyDhQ
8vW4nfkCgYEA7wm0Kl3cg7xKs22QtB1stGur3wCiaNauoKtilnlOFTdbgVF9dsJB
sq6OPK+OITkQXVTNUtFujirsS64Jlr9UdZ5l93eMFzseM32KhpVOSBX8AqLi/LZs
fm6jCCGA1TR+Rvekfd2iKQR32Oq3uZR++Zr68pk7uNBFGxOKM8W8bAMCgYEA7CAu
fDP8TTJXRH5gTKFGpMrULzNYhdqlvRLO5aSeWENnq8sOrpNW4yq9uKYv0/cXttab
e/CFVYH1OkTucyUuTLGw3MNpYk61umXIFzMaW/o++M8gkDWACR+zwj2gha0WGa0Q
04qJEqlJH9SnZ8m7YEMKgRS2r39opui/bWpONxUCgYBsums7Aiq1uUX5S5MQennh
r0AkVXOKYGxaJNrZOyArQlza+6goBsA/eGq2a9wofH5XFaW3UBALlraYzfcKnMjc
H0qeP8B3KKraHPaPtQZAf897m3/IF2pOMCD0J9kkIZZ2zVoC7nc+VQv2nP0o6sS+
4KHZC55AuGtWn5KzbfQA5QKBgF0UCn73VxtvHqtnTbqnUFuhgKbijKCnIfI4OcqY
a7rLR1CXCMCUYAnITWU+TVg27OgsDLp8g3LDedFwXraRD4E4Aknj1eTktgo2GPvc
LyXWrYAS1flCvafbEVceR+qp4i5Y5GsfDw2GIcckYqEtCmnVw4xCiAkCJlS1JtCQ
uShJAoGAXMnqK51x0FRPuG23lbYzBSYZstLfY+wzzpmPQANkfzQCeJVzpbExrahx
R0vEOCX0M9qMvW6zlIa+TnPi04iCo9NPcysgubFUufNTBz89v+Xfl9kXqHeJMT4j
Ztj8w6eKRmeLlLdGuRpFBQ6CcYGY9a5fJ9MmHGMvoQ+A3MuEM6U=
-----END RSA PRIVATE KEY-----"""

    # Note that that the only app currently supported is the Android
    # Authenticator SDK demo app
    # https://github.com/iovation/launchkey-android-authenticator-sdk/tree/master/demo-app
    context.sample_app_apk_path = '/path/to/sample-app.apk'

    # You can use Kobiton Testing
    context.kobiton_username = "username"
    context.kobiton_sdk_key = "83aab95e-c577-410d-a7db-c7a83bd2433a"

    # Or Local Testing
    context.appium_url = 'http://localhost:4723/wd/hub'
    context.platform_name = 'Android'
    context.platform_version = '8.0.0'
    context.device_name = 'Pixel'

    base_before_all(context)


def after_all(context):
    base_after_all(context)


def before_feature(context, feature):
    base_before_feature(context, feature)


def after_feature(context, feature):
    base_after_feature(context, feature)


def before_scenario(context, scenario):
    base_before_scenario(context, scenario)


def after_scenario(context, scenario):
    base_after_scenario(context, scenario)
