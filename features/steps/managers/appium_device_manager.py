from appium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.wait import TimeoutException
from appium.webdriver.webdriver import MobileBy


class AppiumDeviceManager:

    def __init__(self, appium_url, device_capabilities, app_package,
                 timeout_period=10):
        self.driver = webdriver.Remote(appium_url, device_capabilities)
        self.app_package = app_package
        self.timeout_period = timeout_period

    def get_element_by_text(self, text):
        wait = WebDriverWait(self.driver, self.timeout_period)
        try:
            return wait.until(
                EC.presence_of_element_located(
                    (MobileBy.ANDROID_UIAUTOMATOR,
                     'new UiSelector().textContains("%s")' % text)))
        except TimeoutException:
            raise TimeoutException(
                u'Couldn\'t find the text "%s" '
                u'before the timeout of %s seconds' %
                (text, self.timeout_period))

    def get_scrollable_element_by_text(self, text):
        wait = WebDriverWait(self.driver, self.timeout_period)
        try:
            return wait.until(
                EC.presence_of_element_located(
                    (
                        MobileBy.ANDROID_UIAUTOMATOR,
                        'new UiScrollable(new UiSelector().scrollable(true).'
                        'instance(0)).scrollIntoView(new UiSelector().'
                        'textContains("%s").instance(0))' % text)))
        except TimeoutException:
            raise TimeoutException(
                u'Couldn\'t find the text "%s" before the '
                u'timeout of %s seconds' % (
                    text, self.timeout_period))

    def get_element_by_id(self, resource_id):
        wait = WebDriverWait(self.driver, self.timeout_period)
        try:
            return wait.until(
                EC.presence_of_element_located(
                    (
                        MobileBy.ANDROID_UIAUTOMATOR,
                        'new UiSelector().resourceId("%s:id/%s")' % (
                            self.app_package, resource_id))))
        except TimeoutException:
            raise TimeoutException(
                u'Couldn\'t find the id "%s" before the '
                u'timeout of %s seconds' % (resource_id, self.timeout_period))

    def quit(self):
        self.driver.quit()

    def reset(self):
        self.driver.reset()
