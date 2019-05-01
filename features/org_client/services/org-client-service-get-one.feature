Feature: Organization clients can get an Organization Services
  In order to provide for management of Organization Service entities
  As an Organization client
  I can get an Organization Services

  Scenario: Client can retrieve a single Service
    Given I created a Organization Service with the following:
      | key          | value                             |
      | description  | Super Awesome Service             |
      | icon         | https://www.iovation.com/icon     |
      | callback_url | https://www.iovation.com/callback |
      | active       | True                              |
    When I retrieve the created Organization Service
    Then the Organization Service name is the same as was sent
    And the Organization Service description is "Super Awesome Service"
    And the Organization Service icon is "https://www.iovation.com/icon"
    And the Organization Service callback_url is "https://www.iovation.com/callback"
    And the Organization Service is active

  Scenario: Get an invalid Service raises an exception
    When I attempt to retrieve the Organization Service with the ID "eba60cb8-c649-11e7-abc4-cec278b6b50a"
    Then a Forbidden error occurs
