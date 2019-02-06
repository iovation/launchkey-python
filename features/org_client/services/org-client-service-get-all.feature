Feature: Organization clients can get a list of all of their Organization Services
  In order to provide for management of Organization Service entities
  As an Organization client
  I can list all my Organization Services

  Scenario: Getting a list of all Services includes the expected data
    Given I created an Organization Service
    When I retrieve a list of all Organization Services
    Then the current Organization Service is in the Services list
