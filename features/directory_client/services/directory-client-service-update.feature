Feature: Directory clients can update Directory Services
  In order to manage Directory Service entities
  As a Directory client
  I can update Directory Services

  Background:
    Given I created a Directory
    And I created a Directory Service with the following:
      | key          | value                             |
      | description  | Super Awesome Service             |
      | icon         | https://www.iovation.com/icon     |
      | callback_url | https://www.iovation.com/callback |
      | active       | True                              |

  Scenario: Client can update all Directory attributes other than ID and name
    When I update the Directory Service with the following:
      | key          | value                                |
      | description  | So Much Awesome                      |
      | icon         | https://www.iovation.com/iconic      |
      | callback_url | https://www.iovation.com/callbackish |
      | active       | False                                |
    And I retrieve the created Directory Service
    Then the Directory Service name is the same as was sent
    And the Directory Service description is "So Much Awesome"
    And the Directory Service icon is "https://www.iovation.com/iconic"
    And the Directory Service callback_url is "https://www.iovation.com/callbackish"
    And the Directory Service is not active

  Scenario: Attempting to update an invalid Directory Service throws a Forbidden exception
    When I attempt to update the active status of the Directory Service with the ID "eba60cb8-c649-11e7-abc4-cec278b6b50a"
    Then a Forbidden error occurs