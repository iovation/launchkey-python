Feature: Directory Client can list devices
  In order to manage User Devices
  As a Directory Client
  I can list the Devices linked with a User Identifier

  Background:
    Given I created a Directory

  Scenario: Getting the Device list for a User with Devices returns a list of Devices
    Given I made a Device linking request
    When I retrieve the Devices list for the current User
    Then the Device List has 1 Device

  Scenario: Getting the Device list for a User with no Devices returns an empty list
    When I retrieve the Devices list for the user "I do not exist"
    Then the Device List has 0 Devices
