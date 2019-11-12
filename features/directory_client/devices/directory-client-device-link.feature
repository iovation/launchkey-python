Feature: Directory Client can link Devices
  In order to manage User Devices
  As a Directory Client
  I can begin the process for linking a User Identifier and a Device

  Background:
    Given I created a Directory

  Scenario: Linking Devices returns QR Code URL, linking code, and Device ID
    When I make a Device linking request
    Then the Device linking response contains a valid QR Code URL
    And the Device linking response contains a valid Linking Code
    And the Device linking response contains a valid Device ID

  Scenario: Linking Devices with TTL returns QR Code URL and linking code
    When I make a Device linking request with a TTL of 300 seconds
    Then the Device linking response contains a valid QR Code URL
    And the Device linking response contains a valid Linking Code

  Scenario: Linking Devices adds the device to the User's Device list
    When I make a Device linking request
    And I retrieve the Devices list for the current User
    Then there should be 1 Device in the Devices list
    And all of the devices should be inactive

  @device_testing
  Scenario: Linking a physical device
    Given I have added an SDK Key to the Directory
    And I made a Device linking request
    When I link my device
    And I retrieve the Devices list for the current User
    Then there should be 1 Device in the Devices list
    And all of the devices should be active