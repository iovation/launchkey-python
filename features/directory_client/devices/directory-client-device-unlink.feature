Feature: Directory Client can unlink devices
  In order to manage User Devices
  As a Directory Client
  I can unlink a Device from a User Identifier

  Background:
    Given I created a Directory

  Scenario: Unlinking current Device removes it from the Device list
    Given I made a Device linking request
    And I retrieve the Devices list for the current User
    When I unlink the current Device
    And I retrieve the Devices list for the current User
    Then there should be 0 Devices in the Devices list

  Scenario: Unlinking invalid Device throws NotFoundException
    Given I have made a Device linking request
    When I attempt to unlink the device with the ID "67c87654-aed9-11e7-98e9-0469f8dc10a5"
    Then a EntityNotFound error occurs

  Scenario: Unlinking Device from invalid User throws NotFoundException
    When I attempt to unlink the device from the User Identifier "Invalid User"
    Then a EntityNotFound error occurs
