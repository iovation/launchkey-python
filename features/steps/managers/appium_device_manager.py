from appium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.wait import TimeoutException
from appium.webdriver.webdriver import MobileBy


class AppiumDeviceManager:

    def __init__(self, appium_url, device_capabilities, app_package,
                 timeout_period=10):
        """
        Manager for interacting with mobile devices via Appium. Note that
        currently only Android devices are supported.
        :param appium_url: Url to the Appium server
        :param device_capabilities: Dictionary containing Appium device
       capabilities. See: http://appium.io/docs/en/writing-running-appium/caps/
        :param app_package: Path to the
        :param timeout_period: How long to look for an element before timing
        out
        """
        self.driver = webdriver.Remote(appium_url, device_capabilities)
        self.app_package = app_package
        self.timeout_period = timeout_period

    def get_element_by_text(self, text):
        """
        Retrieves a visible element that contains input text.
        :param text: Text to look for
        :raise: selenium.webdriver.support.wait.TimeoutException: The element
        was not found before the timeout_period.
        :return: appium.webdriver.webelement.WebElement
        """
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
        """
        Retrieves a visible element that contains input text. Scrolling to it
        if needed.
        :param text: Text to look for
        :raise: selenium.webdriver.support.wait.TimeoutException: The element
        was not found before the timeout_period.
        :return: appium.webdriver.webelement.WebElement
        """
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
        """
        Retrieves a visible element that matches given ID.
        :param resource_id: ID to look for. It should be the raw id and does
        not need the app package name to be included. IE: demo_link_button
        :raise: selenium.webdriver.support.wait.TimeoutException: The element
        was not found before the timeout_period.
        :return: appium.webdriver.webelement.WebElement
        """
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
        """
        Quits the driver and closes every associated window.
        :return: None
        """
        self.driver.quit()

    def reset(self):
        """
        Resets the current application on the device.
        :return: None
        """
        self.driver.reset()
