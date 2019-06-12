Feature: Organization clients can get a Directory
  In order to provide for retrieving of individual Directory entities
  As an Organization client
  I can get a Directory

  Background:
    Given I created a Directory

  Scenario: Getting a directory returns the correct data
    Given I updated the Directory as active
    And I updated the Directory Android Key with "Hello Android"
    And I updated the Directory iOS P12 with a valid certificate
    And I updated the Directory webhook url to "https://a.webhook.url/path"
    And I generated and added 2 SDK Keys to the Directory
    And I added 2 Services to the Directory
    When I retrieve the created Directory
    Then the ID matches the value returned when the Directory was created
    And the Directory name is the same as was sent
    And the Directory is active
    And the Directory Android Key is "Hello Android"
    And Directory the iOS Certificate Fingerprint matches the provided certificate
    And the Directory has the added SDK Key
    And the Directory has the added Service IDs
    And the Directory webhook url is "https://a.webhook.url/path"

  Scenario: Get an invalid Directory raises an exception
    When I attempt retrieve the Directory identified by "eba60cb8-c649-11e7-abc4-cec278b6b50a"
    Then a Forbidden error occurs
