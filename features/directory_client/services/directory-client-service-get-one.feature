Feature: Directory clients can get an Directory Service
  In order to provide for management of Directory Service entities
  As a Directory client
  I can get an Directory Service

  Background:
    Given I created a Directory

  Scenario: Client can retrieve a single Service
    Given I created a Directory Service with the following:
      | key          | value                             |
      | description  | Super Awesome Service             |
      | icon         | https://www.iovation.com/icon     |
      | callback_url | https://www.iovation.com/callback |
      | active       | True                              |
    When I retrieve the created Directory Service
    Then the Directory Service name is the same as was sent
    And the Directory Service description is "Super Awesome Service"
    And the Directory Service icon is "https://www.iovation.com/icon"
    And the Directory Service callback_url is "https://www.iovation.com/callback"
    And the Directory Service is active

  Scenario: Get an invalid Service raises an exception
    When I attempt to retrieve the Directory Service with the ID "eba60cb8-c649-11e7-abc4-cec278b6b50a"
    Then a Forbidden error occurs
