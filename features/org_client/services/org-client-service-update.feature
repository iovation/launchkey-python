Feature: Organization clients can update Organization Services
  In order to manage Organization Service entities
  As an Organization client
  I can update Organization Services

  Background:
    Given I created a Organization Service with the following:
      | key          | value                             |
      | description  | Super Awesome Service             |
      | icon         | https://www.iovation.com/icon     |
      | callback_url | https://www.iovation.com/callback |
      | active       | True                              |

  Scenario: Client can update all attributes other than ID and name
    When I update the Organization Service with the following:
      | key          | value                                |
      | description  | So Much Awesome                      |
      | icon         | https://www.iovation.com/iconic      |
      | callback_url | https://www.iovation.com/callbackish |
      | active       | False                                |
    And I retrieve the created Organization Service
    Then the Organization Service name is the same as was sent
    And the Organization Service description is "So Much Awesome"
    And the Organization Service icon is "https://www.iovation.com/iconic"
    And the Organization Service callback_url is "https://www.iovation.com/callbackish"
    And the Organization Service is not active

  Scenario: Attempting to update an invalid Organization Service throws a Forbidden exception
    When I attempt to update the active status of the Organization Service with the ID "eba60cb8-c649-11e7-abc4-cec278b6b50a"
    Then a Forbidden error occurs