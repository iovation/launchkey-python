Feature: Organization clients can remove Organization Service Public Keys
  In order to manage the Public Keys in the Organization Service Public Key rotation
  As an Organization client
  I can remove a Public Key from an Organization Service

  Background:
    Given I created an Organization Service
    And I added a Public Key to the Organization Service

  Scenario: Removing Public Key actually removes from list
    Given I added another Public Key to the Organization Service
    When I remove the current Organization Service Public Key
    And I retrieve the current Organization Service's Public Keys
    Then the last current Organization Service's Public Key is not in the list

  Scenario: Removing the last Public Key throws LastRemainingKey exception
    When I attempt to remove the current Organization Service Public Key
    Then a LastRemainingKey error occurs

  Scenario: Attempting to update a Public Key for an invalid Service throws a Forbidden exception
    When I attempt to remove a Public Key from the Organization Service with the ID "eba60cb8-c649-11e7-abc4-cec278b6b50a"
    Then a Forbidden error occurs

  Scenario: Attempting to update an invalid Public Key for a Service throws a Forbidden exception
    When I attempt to remove a Public Key identified by "aa:bb:cc:dd:ee:ff:11:22:33:44:55:66:77:88:99:00" from the Organization Service
    Then a PublicKeyDoesNotExist error occurs
