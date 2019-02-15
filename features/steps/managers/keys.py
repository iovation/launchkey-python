from .base import BaseManager
from base64 import decodebytes


class KeysManager:
    base_64_encoded_alpha_p12 = "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"
    base_64_encoded_beta_p12 = "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"
    alpha_certificate_fingerprint = "7A:31:98:AD:89:68:19:63:39:75:34:A2:E6:9A:00:4E:42:DB:E0:33:7C:14:57:5D:C0:E5:90:B9:36:DD:BB:FA"
    beta_certificate_fingerprint = "BA:F6:DC:B0:0D:35:48:F9:EB:61:DC:78:B7:BE:4F:5C:83:63:A9:C2:B8:1F:A8:B0:F0:A7:47:D1:78:9B:FB:C7"
    alpha_public_key = decodebytes(
        b"LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0NCk1JSUNJakFOQmdrcWhraUc5dzBCQVFFRkFBT0NBZzhBTUlJQ0NnS0NBZ0VBcEVVZHdGQ1EvZWEwdDBQVlk1QkMNCnBhREdiQ1EyM0hteHpXSElXalp0UTRIN2VjSEg3SkVTMXgzQm56RWZWS2FlRG9TeDYydGRiYTBFdFNYUW43TUQNClhiMzMvdGNzUlpEV1kvK2JDb0VXV0FzTUJFVkV1Rzk2dTQ4R3RPU3dnRXd0aUtEaGRXeGNMamx2d3RWaUh0MjYNCmZjTjgxaExDTDFLQVJqeVlxTldHb3ZJSjRrdGx2MkEyU2djYmNJUkV2aUJrK3pTbk02elcvTE1LOTNvN2dmR0gNCk0zSTVNZy9kTEY2b0lyVzNmWk5SYUd3UzZRbzdCbEl6aTJ6bXFxaE5iZ2NmTUY1Zk1nWHhONFkvc2cyL09nWDANClN3VllISUdKK3ZwajFPMkhJTWQycVhpdTQrZVcyd3Q5VGp4SUNBbHd0S1RxZ29Yc3c2UXFjMzJwUTRmT3VrTU4NClBiNUR2REhoT0RFWHF0b0x4UkpPQytpd21OVTdwVStqemV2VlBXRnZ1ZlR4bS9jRnVlTVJpSTkwR2ExQmYvYmQNCkZrNGg1OEd5R3NxbklPTndQd0o2SVFwbW9BTExuSHFDUGZYcXhtT0FQMThkemoxZkFpTEp1SVMwZW02QlJkajANCjdiK1NUZW0rTVZrYmFPOXRyVU10OHkrYzNWeVV4TGZVSS9sQXQ3YWt1Y2JjWmJZc2pHT3QrbUV5MDVIY1NsSWYNCnN2UHZGeElWVEQvVUk3bzIvSzc0M0pjc21adTF2REZqQ2JEcXJTL21VaFkzeXJ4TmJoamlMei9vdU9QTWkrelUNCjR3N0NIcnJrTGhHMHlvSXllSXg0Zk1iNU1OczhFSEx1ZkswRjMzNmd3NE9ZYW5DUlEvdzIvZHdMWE1rM1JtbXENCkVwRzYydTFtMU03V0g1RE5zdTZ1cHRNQ0F3RUFBUT09DQotLS0tLUVORCBQVUJMSUMgS0VZLS0tLS0NCg==")
    beta_public_key = decodebytes(
        b"LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0NCk1JSUNJakFOQmdrcWhraUc5dzBCQVFFRkFBT0NBZzhBTUlJQ0NnS0NBZ0VBeUNzeVlRNlM5MUp4cnRGWUROaUoNCjNIaDlmT1ZVR0RMVmUxQVBxdXpzVkYxQUxmR0lSbnpYaUp3WEk2V2VYTFZvMFJTKzZqSGl6RXluU3FNOURyb1UNCnhjUVNmTzJEMGpmR0c2RVAxQ3R0Y05wY05sQ3huOEg3NURQVllxSWtNWFVUNmoyaVgrbmx2anNYMXZVVVpKOG0NCnRVZVRoTndEb3ZISm0xWTIwdFVkNGRpRC9oYmhOd1lEZXpUbGc3R09CVTdqeUFqTUlSQWtQUEk1MThWd3BSWUUNCjNHclhkekk5Sm5hblZrcHNMVlEyVS9Jdk9NSUNRZC8vanpmMUQ4MU5VQnVzZWdrRnVTUkRBNHMxc3NpTUEyMTYNCkkveDk4TzRsSU8vb0VrdnRnTnF2L2RjaVlDR2VHSHo1bmJ0VlFUdjhpOVlJL1MvS3kvK2lTaGw4dmN2LzYydkMNCmNBaWJSTElIMlA1ZmVsUnluZlQwdTZweW13UUFsellMck1KSERadW5uTVBCUmtoMjRSc1krbFYzTSszc1hrUlgNCnJIVXEyS05DbVAwYXBqVmg3TDRUK0dpdjVyRHJtUzRXTEV4ZmRGMHlNdUU5dFBNQitaU05FZ09Vd3pXVCtqWEkNCnpzOVVuY01rNFFIV2JOdHdSM1ZTa0lDNGwraC9LclVFbWhRQThjV0lZMEs4LzRtTmdtUnh1cFdzNTg4YXdKaUgNCkV1UjMzY2JDM1dZck9kOCs0RkRSR04xUk1POWhrQU1iVm5lSmdobTE2dkh3WHhCbWVoTGczNkErNXI5MTYyRDYNCmVRODUyczNTU01UYjVXbnBBSXJlZUFDejllcFFrM2FZck15Nk85djZxK1Z2VDlJeEpwc2VKNzF5Z1NRVy9RSkENCk1PWWRLaHRwYmcyZnAxdjlOSnR6ZWRjQ0F3RUFBUT09DQotLS0tLUVORCBQVUJMSUMgS0VZLS0tLS0NCg==")
    alpha_md5_fingerprint = "e6:60:3f:95:ea:c8:4d:2b:98:18:c0:0c:28:e8:9f:bb"
    beta_md5_fingerprint = "ee:6d:27:3f:6f:a2:42:94:33:d6:2a:12:a0:4d:1f:56"
