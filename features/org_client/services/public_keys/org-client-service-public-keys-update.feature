Feature: Organization clients can update Organization Service Public Keys
  In order to manage the Public Keys in the Organization Service Public Key rotation
  As an Organization client
  I can update a Public Key for an Organization Service

  Background:
    Given I created an Organization Service

  Scenario: Updating active flag actually updates the record
    Given I added a Public Key to the Organization Service which is active and expires on "2000-01-01T00:00:00Z"
    When I updated the Organization Service Public Key to inactive
    And I retrieve the current Organization Service's Public Keys
    Then the Organization Service Public Key is inactive

  Scenario: Updating expires actually updates the record
    Given I added a Public Key to the Organization Service which is active and expires on "2000-01-01T00:00:00Z"
    When I updated the Organization Service Public Key expiration date to "2001-02-03T04:05:06Z"
    And I retrieve the current Organization Service's Public Keys
    Then the Organization Service Public Key Expiration Date is "2001-02-03T04:05:06Z"

  Scenario: Attempting to update a Public Key for an invalid Service throws a Forbidden exception
    Given I added a Public Key to the Organization Service
    When I attempt to update a Public Key for the Organization Service with the ID "eba60cb8-c649-11e7-abc4-cec278b6b50a"
    Then a Forbidden error occurs

  Scenario: Attempting to update an invalid Public Key for a Service throws a Forbidden exception
    Given I added a Public Key to the Organization Service
    When I attempt to update a Public Key identified by "aa:bb:cc:dd:ee:ff:11:22:33:44:55:66:77:88:99:00" for the Organization Service
    Then a PublicKeyDoesNotExist error occurs
