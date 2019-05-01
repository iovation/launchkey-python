class SampleAppDeviceManager:

    def __init__(self, appium_device_manager):
        self.appium_device_manager = appium_device_manager

    def _approve_alert(self):
        self.appium_device_manager.click(text="OK")

    def unlink_device(self):
        self.appium_device_manager.click(text="Unlink 2 (Custom UI)")

    def _open_linking_menu(self):
        self.appium_device_manager.click(text="Link (Custom UI - Manual)")

    def _fill_linking_code(self, linking_code):
        self.appium_device_manager.send_keys(linking_code, text="Linking code")

    def _fill_authenticator_sdk_key(self, sdk_key):
        self.appium_device_manager.send_keys(sdk_key, text="Auth SDK Key")

    def _type_in_device_name(self, device_name):
        self.appium_device_manager.click(text="Use custom device name")
        self.appium_device_manager.send_keys(device_name, id="demo_link_edit_name")

    def _submit_linking_form(self):
        self.appium_device_manager.click(id="demo_link_button")

    def link_device(self, sdk_key, linking_code, device_name=None):
        self._approve_alert()
        self._open_linking_menu()
        self._fill_linking_code(linking_code)
        self._fill_authenticator_sdk_key(sdk_key)
        if device_name:
            self._type_in_device_name(device_name)
        self._submit_linking_form()

    def _open_auth_menu(self):
        self.appium_device_manager.click(text="Check for Requests (XML)")

    def _tap_refresh(self):
        self.appium_device_manager.click(id="menu_refresh")

    def _approve_auth(self):
        self.appium_device_manager.long_press(id="auth_info_action_positive")

    def _deny_auth(self):
        self.appium_device_manager.long_press(id="auth_info_action_negative")
        self.appium_device_manager.click(text="I don't approve")
        self.appium_device_manager.long_press(id="auth_do_action_negative")

    def approve_request(self):
        self._open_auth_menu()
        self._tap_refresh()
        self._approve_auth()

    def deny_request(self):
        self._open_auth_menu()
        self._tap_refresh()
        self._deny_auth()

    def _dismiss_failure_message(self):
        self.appium_device_manager.click(text="DISMISS")

    def receive_and_acknowledge_auth_failure(self):
        self._open_auth_menu()
        self._tap_refresh()
        self._dismiss_failure_message()
