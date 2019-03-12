Feature: Organization clients can retrieve a list of Public Keys for an Organization Service
  In order to manage the Public Keys in the Organization Service Public Key rotation
  As an Organization client
  I can get a list of Public Keys for an Organization Service

  Background:
    Given I created an Organization Service

  Scenario: No Public Keys returns an empty list
    When I retrieve the current Organization Service's Public Keys
    Then the Organization Service Public Keys list is empty

  Scenario: Adding a Public Key to an Organization Service works
    Given I added a Public Key to the Organization Service which is inactive and expires on "2000-01-01T00:00:00Z"
    When I retrieve the current Organization Service's Public Keys
    Then the Public Key is in the list of Public Keys for the Organization Service
    And the Organization Service Public Key is inactive
    And the Organization Service Public Key Expiration Date is "2000-01-01T00:00:00Z"

  Scenario: Attempting to get the Public Keys for an invalid Organization Service throws a Forbidden exception
    When I attempt to retrieve the Public Keys for the Organization Service with the ID "eba60cb8-c649-11e7-abc4-cec278b6b50a"
    Then a Forbidden error occurs
