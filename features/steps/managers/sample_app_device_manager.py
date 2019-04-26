from selenium.webdriver.support.wait import TimeoutException


class SampleAppDeviceManager:

    def __init__(self, appium_device_manager):
        self.appium_device_manager = appium_device_manager

    def _approve_alert(self, optional=True):
        try:
            self.appium_device_manager.get_element_by_text("OK").click()
        except TimeoutException:
            if optional is False:
                raise Exception("Could not find alert")

    def unlink_device(self):
        self.appium_device_manager.get_scrollable_element_by_text("Unlink 2 (Custom UI)").click()

    def _open_linking_menu(self):
        self.appium_device_manager.get_scrollable_element_by_text(
            "Link (Custom UI - Manual)").click()

    def _fill_linking_code(self, linking_code):
        self.appium_device_manager.get_element_by_text("Linking code").send_keys(linking_code)

    def _fill_authenticator_sdk_key(self, sdk_key):
        self.appium_device_manager.get_element_by_text("Auth SDK Key").send_keys(sdk_key)

    def _type_in_device_name(self, device_name):
        self.appium_device_manager.get_element_by_text("Use custom device name").click()
        self.appium_device_manager.get_element_by_id("demo_link_edit_name").send_keys(device_name)

    def _submit_linking_form(self):
        self.appium_device_manager.get_element_by_id("demo_link_button").click()

    def link_device(self, sdk_key, linking_code, device_name=None):
        self._approve_alert()
        self._open_linking_menu()
        self._fill_linking_code(linking_code)
        self._fill_authenticator_sdk_key(sdk_key)
        if device_name:
            self._type_in_device_name(device_name)
        self._submit_linking_form()

    def _open_auth_menu(self):
        self.appium_device_manager.get_scrollable_element_by_text("Check for Requests (XML)").click()

    def _tap_refresh(self):
        self.appium_device_manager.get_element_by_id("menu_refresh").click()

    def _approve_auth(self):
        self.appium_device_manager.get_element_by_id("auth_info_action_positive").click()

    def _deny_auth(self):
        self.appium_device_manager.get_element_by_id("auth_info_action_negative").click()
        self.appium_device_manager.get_element_by_text("I don't approve").click()
        self.appium_device_manager.get_element_by_id("auth_do_action_negative").click()

    def approve_request(self):
        self._open_auth_menu()
        self._tap_refresh()
        self._approve_auth()

    def deny_request(self):
        self._open_auth_menu()
        self._tap_refresh()
        self._deny_auth()

    def _dismiss_failure_message(self):
        self.appium_device_manager.get_element_by_text("DISMISS").click()

    def receive_and_acknowledge_auth_failure(self):
        self._open_auth_menu()
        self._tap_refresh()
        self._dismiss_failure_message()
