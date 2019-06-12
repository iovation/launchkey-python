Feature: Organization clients can get a list of their Organization Services by ID
  In order to provide for management of Organization Service entities
  As an Organization client
  I can get a list all my Organization Services by ID

  Scenario: Getting a list of Services includes the expected data
    Given I created an Organization Service
    When I retrieve a list of Organization Services with the created Service's ID
    Then the current Organization Service list is a list with only the current Service

  Scenario: Get an invalid Service raises an exception
    When I attempt retrieve a list of Organization Services with the Service ID "eba60cb8-c649-11e7-abc4-cec278b6b50a"
    Then a Forbidden error occurs
