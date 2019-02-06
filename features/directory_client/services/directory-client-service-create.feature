Feature: Directory clients can create Directory Services
  In order to provide for creation of Directory Service entities
  As a Directory client
  I can create Directory Services

  Background:
    Given I created a Directory

  Scenario: Client can send unique Service name and successfully create a Service
    When I create a Directory Service with the following:
      | key          | value                             |
      | description  | Super Awesome Service             |
      | icon         | https://www.iovation.com/icon     |
      | callback_url | https://www.iovation.com/callback |
      | active       | True                              |
    And I retrieve the created Directory Service
    Then the Directory Service name is the same as was sent
    And the Directory Service description is "Super Awesome Service"
    And the Directory Service icon is "https://www.iovation.com/icon"
    And the Directory Service callback_url is "https://www.iovation.com/callback"
    And the Directory Service is active

  Scenario: Client sending duplicate Service name raises ServiceNameInUse
    Given I created a Directory Service
    And I attempt to create a Directory Service with the same name
    Then a ServiceNameTaken error occurs