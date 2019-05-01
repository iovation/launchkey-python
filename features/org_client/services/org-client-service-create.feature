Feature: Organization clients can create Organization Services
  In order to provide for creation of Organization Service entities
  As an Organization client
  I can create Organization Services

  Scenario: Client can send unique Service name and successfully create a Service
    When I create an Organization Service
    And I retrieve the created Organization Service
    Then the Organization Service name is the same as was sent

  Scenario: Client sending duplicate Service name raises ServiceNameInUse
    Given I created an Organization Service
    And I attempt to create a Organization Service with the same name
    Then a ServiceNameTaken error occurs